# from fastapi import FastAPI, Depends, HTTPException
# from sqlalchemy.orm import Session
# from database.connection import get_db
# from database.crud import get_book_by_isbn, get_sentence_by_isbn, add_user_response, get_tags_by_isbn
# from database.schemas import BookSchema, SentenceSchema, UserResponseSchema
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI()

# # CORS 설정
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # 모든 출처 허용 (배포 시 특정 도메인으로 제한 추천)
#     allow_credentials=True,
#     allow_methods=["*"],  # 모든 HTTP 메서드 허용
#     allow_headers=["*"],  # 모든 헤더 허용
# )

# # ✅ 특정 ISBN으로 도서 조회 API
# @app.get("/books/{isbn}", response_model=BookSchema)
# def read_book(isbn: str, db: Session = Depends(get_db)):
#     book = get_book_by_isbn(db, isbn)
#     if book is None:
#         raise HTTPException(status_code=404, detail="해당 ISBN의 도서를 찾을 수 없습니다.")
#     return book

# # ✅ 특정 ISBN으로 생성문장 조회 API
# @app.get("/sentences/{isbn}", response_model=SentenceSchema)
# def read_book(isbn: str, db: Session = Depends(get_db)):
#     sentence = get_sentence_by_isbn(db, isbn)
#     if sentence is None:
#         raise HTTPException(status_code=404, detail="해당 ISBN의 생성문장을 찾을 수 없습니다.")
#     return sentence


# @app.post("/user_responses/")
# def create_user_response(response: UserResponseSchema, db: Session = Depends(get_db)):
#     stmt = add_user_response(response)
#     db.execute(stmt)
#     db.commit()
#     return response

# # 특정 ISBN으로 tags 조회 API
# @app.get("/tags/{isbn}")
# def get_tags(isbn: str, db: Session = Depends(get_db)):
#     tags = get_tags_by_isbn(db, isbn)
#     if tags is None:
#         raise HTTPException(status_code=404, detail="해당 ISBN의 태그를 찾을 수 없습니다.")
#     return {"isbn": isbn, "tags": list(tag[0] for tag in tags)}

    
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
import psycopg2
from database.crud import get_book_by_isbn, get_sentence_by_isbn, add_user_response, get_tags_by_isbn
from database.schemas import BookSchema, SentenceSchema, UserResponseSchema
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from services.book_rec_module import load_embeddings, select_books, \
    update_data, get_message_by_id, weighted_sampling, get_choice_bool, get_sentence_from_db
import json
from typing import Optional
from dotenv import load_dotenv
import os
from app.database.connection import database_engine
# .env 파일 로드
load_dotenv()

# 환경 변수 가져오기
host = os.getenv("HOST")
port = os.getenv("PORT")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
database_name = os.getenv("DATABASE_NAME")

#cursor 설정
engine_for_cursor = database_engine(host, port, user, password, database_name)

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from services.book_rec_module import load_embeddings, select_books, \
    update_data, get_message_by_id, weighted_sampling, get_choice_bool, get_sentences_from_db
from 

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용 (배포 시 특정 도메인으로 제한 추천)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# Global variables for the session
presented_books = set()
round_num = 0
alpha = None
beta_values = None
# book_embeddings = None
# ids = None
book_data = None
user_id = None
question_number = None
cluster_to_books = None
initial_prob = 0.3
decay_factor = 0.9
uncertainty_factor = 10
noise_factor = 0.01
embedding_save_path = "notebook/notebook/data/book_embeddings.npz"

num_clusters = 10


@app.get("/")
def read_root():
    return {"message": "Welcome to the API!"}


@app.get("/books/{isbn}")
def get_book(isbn: str, db: Session = Depends(get_db)):
    if len(isbn) != 13 or not isbn.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Invalid ISBN format. ISBN must be a 13-digit number."
        )
    
# Global variables for the session
round_num = 0
alpha = None
beta_values = None
presented_books = set()
book_embeddings = None
ids = None
book_data = None
user_id = None
question_number = None
cluster_to_books = None
initial_prob = 0.3
decay_factor = 0.9
uncertainty_factor = 10
noise_factor = 0.01


def first_setting_of_logic(user_id, num_clusters, embedding_save_path):
    global round_num, alpha, beta_values, presented_books, book_embeddings, ids, book_data, cluster_to_books
    embedding_save_path = "notebook/notebook/data/book_embeddings.npz"  # 저장된 파일 경로
    # llm_output_path = 'data/scraping/llm_output_fixed.json'

    ids, book_embeddings = load_embeddings(embedding_save_path)
    # book_data = load_book_data(llm_output_path)

     # ✅ DB 연결 후 책 데이터 불러오기
    db: Session = next(get_db())
    book_data = get_sentences_from_db(db)  # ✅ `id, isbn, sentence`만 가져오기
    db.close()  # 사용 후 세션 닫기

    books = [f"Book {i}" for i in range(len(ids))]  # books는 ids의 길이에 따라 생성
    assert len(books) == len(ids), "Books length mismatch with IDs! "
    num_books = len(book_embeddings)

    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    clusters = kmeans.fit_predict(book_embeddings)

    # 각 클러스터의 책 인덱스 저장
    cluster_to_books = {i: [] for i in range(num_clusters)}
    for idx, cluster_id in enumerate(clusters):
        cluster_to_books[cluster_id].append(idx)

    alpha = np.ones(num_books)
    beta_values = np.ones(num_books)

    round_num = 0
    question_number = round_num + 1
    return ids, book_embeddings, book_data, user_id, question_number, cluster_to_books


def suggest_books(book_embeddings, cluster_to_books, exploration_prob, noise_factor, book_choice):
    global round_num
    if round_num < 30:  # 초반 10 라운드 동안 지수적 감소
        exploration_prob = initial_prob * (decay_factor ** round_num)
    else:  # 이후에는 UCB 기반 조정
        total_selections = len(presented_books)
        exploration_prob = uncertainty_factor / (uncertainty_factor + total_selections)

    book_a, book_b = select_books(book_embeddings, cluster_to_books, alpha, 
                                    beta_values, presented_books, exploration_prob, 
                                    noise_factor, book_choice)
    return book_a, book_b


@app.get("/books/{isbn}", response_model=BookSchema)
def read_book(isbn: str, db: Session = Depends(get_db)):
    book = get_book_by_isbn(db, isbn)
    if book is None:
        raise HTTPException(
            status_code=404,
            detail=f"Book with ISBN {isbn} not found."
        )
    return book

@app.get("/sentences/{isbn}", response_model=SentenceSchema)
def read_sentence(isbn: str, db: Session = Depends(get_db)):
    sentence = get_sentence_by_isbn(db, isbn)
    if sentence is None:
        raise HTTPException(status_code=404, detail="해당 ISBN의 생성문장을 찾을 수 없습니다.")
    return sentence


@app.post("/user_responses/")
def create_user_response(response: UserResponseSchema, db: Session = Depends(get_db)):
    stmt = add_user_response(response)
    db.execute(stmt)
    db.commit()
    return response


@app.get("/recommendation/{user_id}")
def get_recommendations(user_id: str, db: Session = Depends(get_db)):
    # 초기화 및 추천 시작
    global round_num, initial_prob, decay_factor, uncertainty_factor, alpha, beta_values, presented_books, noise_factor, ids, book_data, cluster_to_books, question_number
    num_clusters = 6  # 클러스터 수
    embedding_save_path = "notebook/notebook/data/book_embeddings.npz"
    # llm_output_path = 'data/scraping/llm_output_fixed.json'

    ids, book_embeddings, book_data, user_id, question_number, cluster_to_books = first_setting_of_logic(user_id, num_clusters, embedding_save_path)

    book_a, book_b = suggest_books(book_embeddings, cluster_to_books, initial_prob, noise_factor, None)

    # 책 선택 (이 부분은 실제 구현에서는 사용자의 선택을 받아서 처리)
    book_choice_updated = None
    choice_bool = get_choice_bool(user_id, question_number)
    if choice_bool[0]:
        book_choice_updated = book_a
    elif choice_bool[1]:
        book_choice_updated = book_b
    else:
        book_choice_updated = None

    if book_choice_updated:
        update_data(choice_bool, book_a, book_b, alpha, beta_values)

    round_num += 1  # 라운드 업데이트

    return {
        "round": round_num,
        "book_a": get_message_by_id(ids, ids[book_a], book_data),
        "book_b": get_message_by_id(ids, ids[book_b], book_data),
    }
