from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
import psycopg2
from database.crud import get_book_by_isbn, get_sentence_by_isbn, add_user_response, get_tags_by_isbn, get_question_number_by_user_id
from database.schemas import BookSchema, SentenceSchema, UserResponseSchema
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from services.book_rec_module import load_embeddings, select_books, \
    update_data, get_message_by_id, weighted_sampling, get_choice_bool, get_sentence_from_db
from dotenv import load_dotenv
import os
from app.database.connection import database_engine
from fastapi.responses import JSONResponse

# .env 파일 로드
load_dotenv()

# 환경 변수 가져오기
host = os.getenv("HOST")
port = os.getenv("POSTGRES_PORT")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
database_name = os.getenv("DATABASE_NAME")

#cursor 설정
engine_for_cursor = database_engine(host, port, user, password, database_name)

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
book_data = None
user_id = None
question_number = 0
cluster_to_books = None
initial_prob = 0.3
decay_factor = 0.9
uncertainty_factor = 10
noise_factor = 0.01
embedding_save_path = "notebook/notebook/data/book_embeddings.npz"

num_clusters = 10

@app.get("/books/{isbn}")
def get_book(isbn: str, db: Session = Depends(get_db)):
    if len(isbn) != 13 or not isbn.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Invalid ISBN format. ISBN must be a 13-digit number."
        )
    
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


@app.get("/final_recommendation/{user_id}")
def get_recommendations(user_id: str):
    selected_books = np.array(list(presented_books)[-5:])
    selected_embeddings = book_embeddings[selected_books]
    weights = np.arange(1, len(selected_books) + 1)  # 가중치 추가  ######### 다시 볼 필요 있음
    preference_center = np.average(selected_embeddings, axis=0, weights=weights).reshape(1, -1)


    # 중심과 유사한 책 추천 (코사인 유사도 기준)
    similarities = cosine_similarity(preference_center, book_embeddings).flatten()
    final_recommendations = weighted_sampling(similarities, num_samples=10, temperature=0.2)

    return final_recommendations

def first_setting_of_logic(user_id, num_clusters, embedding_save_path, db):
    global round_num, alpha, beta_values, presented_books, book_embeddings, ids, book_data, cluster_to_books
    # embedding_save_path = "notebook/notebook/data/book_embeddings.npz" 
    embedding_save_path = "embedding/book_embeddings.npz"  # 저장된 파일 경로

    ids, book_embeddings = load_embeddings(embedding_save_path)

    book_data = get_sentence_from_db(db)

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

    # round_num = 0
    # question_number = round_num + 1
    return ids, book_embeddings, book_data, user_id, cluster_to_books


def suggest_books(book_embeddings, cluster_to_books, noise_factor, book_choice=None):
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

@app.get("/question_number/{user_id}", response_model=BookSchema)
def get_question_number(user_id: str, db: Session = Depends(get_db)):
    question_number = get_question_number_by_user_id(db, user_id)
    if question_number is None:
        raise HTTPException(
            status_code=404,
            detail=f"Book with ISBN {user_id} not found."
        )
    return question_number



def choice_arrange(user_id, question_number, book_a, book_b):
    cursor = get_cursor(host, port, user, password, database_name)
    choice_bool = get_choice_bool(cursor,user_id, question_number)

    if choice_bool[0]:
        choice = 'a'
    elif choice_bool[1]:
        choice = 'b'
    else:
        choice = None

    # 데이터 업데이트
    if choice:
        book_choice = update_data(choice, book_a, book_b, alpha, beta_values)
        return book_choice
    else:
        update_data(choice, book_a, book_b, alpha, beta_values)
        return None


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


# @app.get("/recommendation/{user_id}")
# def get_book_suggestions(user_id: str, db: Session = Depends(get_db)):
#     # question_number = get_question_number(user_id, db)
#     # question_number = get_question_number_by_user_id(db, user_id)
    
#     question_number = get_question_number_by_user_id(db, user_id) or 0
#     print('question_number:!!!!!!!!!!!!!!!!!!!!!!!!!!!!' , question_number)
#     # print('question_number--int:!!!!!!!!!!!!!!!!!!!!!!!!!!!!' , int(question_number[0]))


#     if user_id and question_number == 0:
#         ids, book_embeddings, book_data, user_id, question_number, cluster_to_books = first_setting_of_logic(user_id, num_clusters, embedding_save_path, db)
#         book_a, book_b = suggest_books(book_embeddings, cluster_to_books, noise_factor)

#         book_a_isbn =  get_isbn_by_id(ids, ids[book_a], book_data)
#         book_b_isbn =  get_isbn_by_id(ids, ids[book_b], book_data)
        
#         message_a = get_message_by_id(ids, ids[book_a], book_data)
#         message_b = get_message_by_id(ids, ids[book_b], book_data)
    

#     elif user_id and question_number > 0 :
#         try:
#             print("book_a before assignment:", book_a)

#             book_choice_updated = choice_arrange(user_id, question_number, book_a, book_b)
#             book_a, book_b = suggest_books(book_embeddings, cluster_to_books, noise_factor, book_choice_updated)

#             book_a_isbn =  get_isbn_by_id(ids, ids[book_a], book_data)
#             book_b_isbn =  get_isbn_by_id(ids, ids[book_b], book_data)

#             message_a = get_message_by_id(ids, ids[book_a], book_data)
#             message_b = get_message_by_id(ids, ids[book_b], book_data)

#         except Exception as e:
#             print(f"An error occurred: {e}")
#             raise HTTPException(status_code=500, detail="Internal Server Error")
@app.get("/recommendation/{user_id}")
def get_book_suggestions(user_id: str, db: Session = Depends(get_db)):
    question_number = get_question_number_by_user_id(db, user_id)
    print('question_number:!!!!!!!!!!!!!!!!!!!!!!!!!!!!', question_number)

    # 변수 초기화
    book_a = None
    book_b = None
    book_a_isbn = None
    book_b_isbn = None
    message_a = None
    message_b = None
    book_embeddings = None
    cluster_to_books = None
    noise_factor = 0
    book_data = None
    ids = 0


    if user_id and question_number == 0:
        ids, book_embeddings, book_data, user_id, cluster_to_books = first_setting_of_logic(user_id, num_clusters, embedding_save_path, db)
        book_a, book_b = suggest_books(book_embeddings, cluster_to_books, noise_factor)
        print("This is if")

    else:
        book_choice_updated = choice_arrange(user_id, question_number, book_a, book_b)
        book_a, book_b = suggest_books(book_embeddings, cluster_to_books, noise_factor, book_choice_updated)
        print("This is else")

    # book_a, book_b가 None이 아닐 때만 실행
    if book_a is not None and book_b is not None:
        book_a_isbn = get_isbn_by_id(ids, ids[book_a], book_data)
        book_b_isbn = get_isbn_by_id(ids, ids[book_b], book_data)

        message_a = get_message_by_id(ids, ids[book_a], book_data)
        message_b = get_message_by_id(ids, ids[book_b], book_data)


    print('\n')
    print(f"Round {question_number + 1}: Choose between:")
    print(f"a: {message_a}")
    print(f"b: {message_b}")

    # ISBN + 문장을 함께 반환
    return JSONResponse(
        content={
            "bookA": {"question_num": question_number, "sentence_id": str(book_a), "isbn": str(book_a_isbn), "sentence": message_a},
            "bookB": {"question_num": question_number, "sentence_id": str(book_b), "isbn": str(book_b_isbn), "sentence": message_b}
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

