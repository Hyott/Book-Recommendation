from services.module import BookRecommendation
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
import psycopg2
from database.crud import get_book_by_isbn, get_sentence_by_isbn, add_user_response, get_tags_by_isbn, get_question_number_by_user_id, get_sentences_by_ids
from database.schemas import BookSchema, SentenceSchema, UserResponseSchema
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

from services.module import BookRecommendation
from dotenv import load_dotenv
import os
from database.connection import database_engine
from fastapi.responses import JSONResponse
from collections import defaultdict

load_dotenv()

host = os.getenv("HOST")
port = os.getenv("POSTGRES_PORT")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
database_name = os.getenv("DATABASE_NAME")

engine_for_cursor = database_engine(host, port, user, password, database_name)

ENV = os.getenv("ENV", "local")
ROOT_PATH = os.getenv("ROOT_PATH", "")

app = FastAPI(root_path=ROOT_PATH, docs_url='/sesac', redoc_url=None, openapi_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용 (배포 시 특정 도메인으로 제한 추천)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

user_book_chosen_dict = defaultdict(lambda: defaultdict(list))

@app.get("/recommendation/{user_id}")
def get_book_suggestions(user_id: str, db: Session = Depends(get_db)):
    bookrecommendation = BookRecommendation(user_id, db)
    suggested_books_indices, question_number = bookrecommendation.get_book_suggestions()
    print(f"suggested_books_indices: {suggested_books_indices}")
    book_a, book_b = get_sentences_by_ids(db, suggested_books_indices)
    
    return JSONResponse(
                content={
                    "bookA": {"question_num": question_number, 
                                "sentence_id": book_a.id, 
                                "isbn": book_a.isbn, 
                                "sentence": book_a.sentence},
                    "bookB": {"question_num": question_number, 
                                "sentence_id": book_b.id, 
                                "isbn": book_b.isbn, 
                                "sentence": book_b.sentence},
                    },
                headers={"Content-Type": "application/json; charset=utf-8"}
            )

@app.get("/final_recommendation/{user_id}")
def get_recommendations(user_id: str, db: Session = Depends(get_db)):
    recommendationEngine = BookRecommendation(user_id, db)
    recommendation_isbns = recommendationEngine.get_final_recommendation()
    return recommendation_isbns


@app.get("/books/{isbn}")
def get_book(isbn: str, db: Session = Depends(get_db)):
    if len(isbn) != 13 or not isbn.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Invalid ISBN format. ISBN must be a 13-digit number."
        )

    book = get_book_by_isbn(db, isbn)
    sentence = get_sentence_by_isbn(db, isbn)
    tags = get_tags_by_isbn(db, isbn)

    # 저자명을 처리
    split_comma_reuslt = book.author.split(',')
    
    if len(split_comma_reuslt) >= 2:
        book_author = f'{split_comma_reuslt[0].strip()} 외 {len(split_comma_reuslt)-1}명 저'
    else:
        book_author = book.author
    if not book:
        raise HTTPException(
            status_code=404,
            detail=f"Book with ISBN {isbn} not found."
        )

    response_data = {
        "isbn": book.isbn,
        "title": book.title,
        "author": book_author,
        "image_url": book.image_url,
        "sentence": sentence.sentence if sentence else None,
        "letter": sentence.letter if sentence else None,
        "tags": [tag.tag_name for tag in tags] if tags else []
    }
    return JSONResponse(content=response_data, media_type="application/json; charset=utf-8")


@app.get("/tags/{isbn}")
def get_tags(isbn: str, db: Session = Depends(get_db)):
    if len(isbn) != 13 or not isbn.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Invalid ISBN format. ISBN must be a 13-digit number."
        )
    
    book = get_tags_by_isbn(db, isbn)
    if book is None:
        raise HTTPException(
            status_code=404,
            detail=f"Book with ISBN {isbn} not found."
        )
    return book


@app.get("/sentences/{isbn}", response_model=SentenceSchema)
def get_sentence_and_letter(isbn: str, db: Session = Depends(get_db)):
    sentence = get_sentence_by_isbn(db, isbn)
    if sentence is None:
        raise HTTPException(status_code=404, detail="해당 ISBN의 생성문장을 찾을 수 없습니다.")

    # SQLAlchemy 객체를 Pydantic 모델로 변환
    sentence_data = SentenceSchema(id=sentence.id, isbn=sentence.isbn, sentence=sentence.sentence)
    
    return JSONResponse(content=sentence_data.model_dump(), headers={"Content-Type": "application/json; charset=utf-8"})


@app.post("/user_responses/")
def create_user_response(response: UserResponseSchema, db: Session = Depends(get_db)):
    stmt = add_user_response(response)
    db.execute(stmt)
    db.commit()
    return response


@app.get("/books/{isbn}", response_model=BookSchema)
def read_book(isbn: str, db: Session = Depends(get_db)):
    book = get_book_by_isbn(db, isbn)
    if book is None:
        raise HTTPException(
            status_code=404,
            detail=f"Book with ISBN {isbn} not found."
        )
    return book


@app.get("/question_number/{user_id}", response_model=BookSchema)
def get_question_number(user_id: str, db: Session = Depends(get_db)):
    question_number = get_question_number_by_user_id(db, user_id)
    if question_number is None:
        raise HTTPException(
            status_code=404,
            detail=f"Book with ISBN {user_id} not found."
        )
    return question_number


def get_message_by_id(ids, book_id, book_data):
    """
    ids와 book_data를 이용해 특정 book_id의 메시지를 조회합니다.
    """
    idx = np.where(ids == book_id)[0][0]  # book_id의 인덱스 찾기
    return book_data[idx]["sentence"]


def get_isbn_by_id(ids, book_id, book_data):
    """
    ids와 book_data를 이용해 특정 book_id의 메시지를 조회합니다.
    """
    idx = np.where(ids == book_id)[0][0]  # book_id의 인덱스 찾기
    return book_data[idx]["isbn"]


def get_cursor(host, port, user, password, database_name):
    conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=database_name
        )
    conn.autocommit = True
    cursor = conn.cursor()
    
    return cursor