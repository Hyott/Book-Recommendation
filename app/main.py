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
    update_data, get_message_by_id, weighted_sampling, get_choice_bool, get_sentence_from_db, get_tournament_winner_cluster_until_round5
from dotenv import load_dotenv
import os
from app.database.connection import database_engine
from fastapi.responses import JSONResponse
from collections import defaultdict

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
user_presented_books = defaultdict(set)
user_suggested_books = defaultdict(list)
user_books_chosen = defaultdict(list)
user_round_num = defaultdict(int)
user_alpha = defaultdict()
user_beta_values = defaultdict()
user_book_chosen_dict = defaultdict(lambda: defaultdict(list))

embedding_save_path = "notebook/notebook/data/book_embeddings.npz"
book_data = None
num_clusters = 6
user_id = None
question_number = 0
cluster_to_books = None

initial_prob = 0.3
decay_factor = 0.9
uncertainty_factor = 10
noise_factor = 0.01



# @app.get("/books/{isbn}")
# def get_book(isbn: str, db: Session = Depends(get_db)):
#     if len(isbn) != 13 or not isbn.isdigit():
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid ISBN format. ISBN must be a 13-digit number."
#         )
    
#     book = get_book_by_isbn(db, isbn)
#     if book is None:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Book with ISBN {isbn} not found."
#         )
#     return book
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

    if not book:
        raise HTTPException(
            status_code=404,
            detail=f"Book with ISBN {isbn} not found."
        )

    # return {
    #     "isbn": book.isbn,
    #     "title": book.title,
    #     "author": book.author,
    #     "image_url": book.image_url,
    #     "category": book.category,
    #     "description": book.description,
    #     "key_sentences": book.key_sentences,
    #     "publication_date": book.publication_date,
    #     "sentence": sentence.sentence if sentence else None,  # ✅ 문장 추가
    #     "letter": sentence.letter if sentence else None,
    #     "tags": [tag.tag_name for tag in tags] if tags else []  # ✅ 태그를 리스트로 변환
    # }

    response_data = {
        "isbn": book.isbn,
        "title": book.title,
        "author": book.author,
        "image_url": book.image_url,
        # "category": book.category,
        # "description": book.description,
        # "key_sentences": book.key_sentences,
        # "publication_date": book.publication_date,
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
    # return sentence

    # SQLAlchemy 객체를 Pydantic 모델로 변환
    sentence_data = SentenceSchema(id=sentence.id, isbn=sentence.isbn, sentence=sentence.sentence)
    
    return JSONResponse(content=sentence_data.model_dump(), headers={"Content-Type": "application/json; charset=utf-8"})


@app.post("/user_responses/")
def create_user_response(response: UserResponseSchema, db: Session = Depends(get_db)):
    stmt = add_user_response(response)
    db.execute(stmt)
    db.commit()
    return response


@app.get("/final_recommendation/{user_id}")
def get_recommendations(user_id: str, db: Session = Depends(get_db)):
    global user_presented_books, book_data
    
    presented_books = user_presented_books[user_id]
    presented_books = list(presented_books)
    print("presented_books : ", presented_books)
    selected_books = presented_books[-5:]
    # selected_embeddings = book_embeddings[selected_books]
    selected_embeddings = np.array([book_embeddings[idx] for idx in selected_books])

    # selected_books = [int(book) for book in selected_books]
    print("selected_books:", selected_books)
    # print("Type of selected_books:", type(selected_books))
    # print("selected_books elements:", [type(i) for i in selected_books])

    weights = np.arange(1, len(selected_books) + 1)  # 가중치 추가  ######### 다시 볼 필요 있음
    preference_center = np.average(selected_embeddings, axis=0, weights=weights).reshape(1, -1)

    # 중심과 유사한 책 추천 (코사인 유사도 기준)
    similarities = cosine_similarity(preference_center, book_embeddings).flatten()
    final_recommendations = weighted_sampling(similarities, num_samples=5, temperature=0.2)

    print("final_recommendations: ", final_recommendations)
    # print("type el final_recommendations :", [type(el) for el in final_recommendations])

    final_recommendations = [get_isbn_by_id(ids, ids[element], book_data) for element in final_recommendations]
    print("final_recommendations: ", final_recommendations)
    print("type el final_recommendations :", [type(el) for el in final_recommendations])

    return final_recommendations

def first_setting_of_logic(user_id, num_clusters, embedding_save_path, db, user_alpha, user_beta_values ):
    global round_num, alpha, beta_values, presented_books, book_embeddings, ids, book_data, cluster_to_books 
    embedding_save_path = "data/book_embeddings.json" 

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

    user_alpha[user_id] = np.ones(num_books)
    user_beta_values[user_id] = np.ones(num_books)

    alpha = user_alpha[user_id]
    beta_values = user_beta_values[user_id]

    return ids, book_embeddings, book_data, user_id, cluster_to_books


def suggest_books(question_number, book_embeddings, cluster_to_books, noise_factor, presented_books, suggested_books, books_chosen, book_chosen_dict, book_choice=None):
    if question_number < 30:  # 초반 10 라운드 동안 지수적 감소
        exploration_prob = initial_prob * (decay_factor ** question_number)
    else:  # 이후에는 UCB 기반 조정
        total_selections = len(presented_books)
        exploration_prob = uncertainty_factor / (uncertainty_factor + total_selections)

    # book_a, book_b = select_books(book_embeddings, cluster_to_books, alpha, 
    #                                 beta_values, presented_books, exploration_prob, 
    #                                 noise_factor, book_choice)
    if 0 <= question_number <= 4:
        book_a, book_b = get_tournament_winner_cluster_until_round5(book_embeddings, cluster_to_books, alpha, 
                                                                    beta_values, presented_books, exploration_prob, 
                                                                    noise_factor, book_choice, question_number, books_chosen, suggested_books)
        return book_a, book_b
    
    else:
        # 가장 많이 선택된 {클러스터 번호 : 책 인덱스} 반환
        def get_top_two_longest_lists(book_chosen_dict):
            # 리스트 길이를 기준으로 정렬 (길이가 같으면 키가 작은 순서)
            sorted_items = sorted(book_chosen_dict.items(), key=lambda x: (len(x[1]), -x[0]), reverse=True)
            # 상위 2개 반환 (최대 2개만)
            return dict(sorted_items[:2])

        sorted_cluster_books = get_top_two_longest_lists(book_chosen_dict)
        print("sorted_cluster_books : ", sorted_cluster_books)
        
        return 1111, 1112

# @app.get("/books/{isbn}", response_model=BookSchema)
# def read_book(isbn: str, db: Session = Depends(get_db)):
#     book = get_book_by_isbn(db, isbn)
#     if book is None:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Book with ISBN {isbn} not found."
#         )
#     return book


@app.get("/question_number/{user_id}", response_model=BookSchema)
def get_question_number(user_id: str, db: Session = Depends(get_db)):
    question_number = get_question_number_by_user_id(db, user_id)
    if question_number is None:
        raise HTTPException(
            status_code=404,
            detail=f"Book with ISBN {user_id} not found."
        )
    return question_number


def choice_arrange(user_id, question_number, book_a, book_b, books_chosen, cluster_to_books, alpha, beta_values, book_chosen_dict):
    cursor = get_cursor(host, port, user, password, database_name)
    choice_bool = get_choice_bool(cursor, user_id, question_number)

    if choice_bool[0]:
        choice = 'a'
    elif choice_bool[1]:
        choice = 'b'
    else:
        choice = None

    # 데이터 업데이트
    if choice:
        book_choice = update_data(choice, book_a, book_b, alpha, beta_values)

        cluster_of_choice = None
        for cluster_id, book_list in cluster_to_books.items():
            if book_choice in book_list:
                cluster_of_choice = cluster_id
                break

        books_chosen.append(book_choice)
        
        book_chosen_dict[cluster_of_choice].append(book_choice)
        print("book_chosen_dict: ", book_chosen_dict)
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

# 알파, 베타 업데이트 여부 확인을 위한 함수
def print_nonone(arr, name):
    """배열에서 1이 아닌 값의 인덱스와 값을 출력하는 함수"""
    nonone_indices = np.where(arr != 1)[0]  # 1이 아닌 값들의 인덱스
    if len(nonone_indices) == 0:
        print(f"{name} 배열에 1이 아닌 값이 없습니다.")
    else:
        print(f"{name} 배열의 1이 아닌 값들:")
        for idx in nonone_indices:
            print(f"Index: {idx}, Value: {arr[int(idx)]}")



@app.get("/recommendation/{user_id}")
def get_book_suggestions(user_id: str, db: Session = Depends(get_db)):
    global cluster_to_books, book_embeddings, book_data, ids, book_a, book_b, \
        exploration_prob, book_choice, \
            user_presented_books, user_suggested_books, user_books_chosen, user_alpha, user_beta_values, user_book_chosen_dict
    
    if user_id not in user_presented_books:
        print(f"New user detected: {user_id}. Initializing presented_books, cluster_to_books and embeddings...")  
        ids, book_embeddings, book_data, user_id, cluster_to_books = first_setting_of_logic(
            user_id, num_clusters, embedding_save_path, db, user_alpha, user_beta_values
        )  

    question_number = get_question_number_by_user_id(db, user_id)
    print('question_number:!!!!!!!!!!!!!!!!!!!!!!!!!!!!', question_number)
    
    presented_books = user_presented_books[user_id]
    suggested_books = user_suggested_books[user_id]
    books_chosen = user_books_chosen[user_id]
    book_chosen_dict = user_book_chosen_dict[user_id]
    round_num = user_round_num[user_id]

    book_a_isbn = None
    book_b_isbn = None
    message_a = None
    message_b = None

    if question_number == 0:
        book_a, book_b = suggest_books(question_number, book_embeddings, cluster_to_books, noise_factor, presented_books, suggested_books, books_chosen, book_chosen_dict)
        print("This is 'if' :", book_a, book_b)
    else:
        print("This is 'else' - first :", book_a, book_b)
        book_choice_updated = choice_arrange(user_id, question_number, book_a, book_b, books_chosen, cluster_to_books,  alpha, beta_values, book_chosen_dict)
        print("book_choice_updated : ", book_choice_updated)
        book_a, book_b = suggest_books(question_number, book_embeddings, cluster_to_books, noise_factor, presented_books, suggested_books, books_chosen, book_chosen_dict, book_choice_updated)
        print("This is 'else' -second :", book_a, book_b)

    # book_a, book_b가 None이 아닐 때만 실행
    if book_a is not None and book_b is not None:
        question_number += 1
        book_a_isbn = get_isbn_by_id(ids, ids[book_a], book_data)
        book_b_isbn = get_isbn_by_id(ids, ids[book_b], book_data)

        message_a = get_message_by_id(ids, ids[book_a], book_data)
        message_b = get_message_by_id(ids, ids[book_b], book_data)


    print('\n')
    print(f"Round {question_number}: Choose between:")
    print(f"a: {message_a}")
    print(f"b: {message_b}")
    print_nonone(alpha, "alpha")
    print_nonone(beta_values, "beta")
    print('\n')

    # ISBN + 문장을 함께 반환
    return JSONResponse(
        content={
            "bookA": {"question_num": question_number, "sentence_id": str(book_a), "isbn": str(book_a_isbn), "sentence": message_a},
            "bookB": {"question_num": question_number, "sentence_id": str(book_b), "isbn": str(book_b_isbn), "sentence": message_b}
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )







