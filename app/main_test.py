from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
import psycopg2
from database.crud import get_book_by_isbn, get_sentence_by_isbn, add_user_response, get_tags_by_isbn, get_question_number_by_user_id
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import os
from app.database.connection import database_engine
from fastapi.responses import JSONResponse
from collections import defaultdict
import joblib
import time

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

ENV = os.getenv("ENV", "local")
ROOT_PATH = os.getenv("ROOT_PATH", "")

# FastAPI 인스턴스 생성 (root_path 적용)
app = FastAPI(root_path=ROOT_PATH, docs_url='/sesac', redoc_url=None, openapi_url=None)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용 (배포 시 특정 도메인으로 제한 추천)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

@app.get("/recommendation/{user_id}")
def get_book_suggestions(user_id: str, db: Session = Depends(get_db)):
    
        

    return JSONResponse(
        content={
            "bookA": {"question_num": question_number, 
                        "sentence_id": str(book_a), 
                        "isbn": str(book_a_isbn), 
                        "sentence": message_a},
            "bookB": {"question_num": question_number, 
                        "sentence_id": str(book_b), 
                        "isbn": str(book_b_isbn), 
                        "sentence": message_b}
            },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
    


@app.get("/final_recommendation/{user_id}")
def get_recommendations(user_id: str, db: Session = Depends(get_db)):
    global question_number, user_book_a, user_book_b,\
        books_chosen, cluster_to_books, book_chosen_dict
    
    question_number = get_question_number_by_user_id(db, user_id)
    print('final_question_number:!!!!!!!!!!!!!!!!!!!!!!!!!!!!', question_number)

    presented_books = user_presented_books[user_id]
    suggested_books = user_suggested_books[user_id]
    books_chosen = user_books_chosen[user_id]
    book_chosen_dict = user_book_chosen_dict[user_id]
    cluster_to_books = user_cluster_to_books[user_id]
    weighted_centroid_2nd = user_weighted_centroid_2nd[user_id]
    book_a = user_book_a[user_id]
    book_b = user_book_b[user_id]
    

    #1 10번째 초이스 함수 돌리고
    book_choice_updated = choice_arrange(user_id, question_number, book_a, book_b, 
                                        books_chosen, cluster_to_books, book_chosen_dict)
    print("book_choice_updated : ", book_choice_updated)
    print("presented_books : ", presented_books)
    print(f"suggested_books :  {suggested_books}")
    print("books_chosen : ", books_chosen)
        

    #2 최종 intergrated_centroid 만들고
    weights_for_final_centroid = np.array([3, 1, 1])  
    vector_of_choice9 = book_embeddings[books_chosen[-2]]
    vector_of_choice10 = book_embeddings[books_chosen[-1]]
    # vector_of_choice8 = book_embeddings[books_chosen[7]]
    all_vectors_final = np.vstack([weighted_centroid_2nd, vector_of_choice9, vector_of_choice10])
    # 가중 평균으로 new_centroid 계산
    weighted_centroid_final = np.average(all_vectors_final, axis=0, weights=weights_for_final_centroid, keepdims=True)
    print(f"weighted_centroid_final : {weighted_centroid_final}")



    def get_top_5_similar_books(weighted_centroid_final, book_embeddings, top_n=25):
        """
        코사인 유사도 기반으로 weighted_centroid_final과 가장 유사한 책 5개 반환
        
        Parameters:
        - weighted_centroid_final (np.ndarray): 중심 벡터 (1, embedding_dim)
        - book_embeddings (np.ndarray): 책 임베딩 벡터 (num_books, embedding_dim)
        - top_n (int): 반환할 유사한 책의 수 (기본값: 5)
        
        Returns:
        - top_indices (list): 가장 유사한 책 인덱스 리스트
        - top_similarities (list): 각 책의 유사도 리스트
        """
        if weighted_centroid_final.ndim == 1:
            weighted_centroid_final = weighted_centroid_final.reshape(1, -1)
        
        # 코사인 유사도 계산
        similarities = cosine_similarity(weighted_centroid_final, book_embeddings)[0]
        
        # 유사도가 높은 순으로 정렬
        top_indices = np.argsort(similarities)[::-1][:top_n]
        top_similarities = similarities[top_indices]

        return top_indices, top_similarities
    
    top_indices, top_similarities = get_top_5_similar_books(weighted_centroid_final, book_embeddings)

    # 중복 제거 (이미 추천한 책 제외)
    filtered_pairs = [(int(idx), float(similarity)) for idx, similarity in zip(top_indices, top_similarities)  if idx not in presented_books][:5]
    unique_indices = [pair[0] for pair in filtered_pairs]
    unique_similarities = [pair[1] for pair in filtered_pairs]

    # 결과 출력
    print(f"Top 5 Similar Books Indices: {unique_indices}")
    print(f"Top 5 Similarities: {unique_similarities}")
    print("final_recommendations_indices: ", unique_indices)

    final_recommendations = [get_isbn_by_id(ids, ids[element], book_data) for element in unique_indices]
    print("final_recommendations_isbn : ", final_recommendations)
    print("type el final_recommendations :", [type(el) for el in final_recommendations])

    return final_recommendations


def first_setting_of_logic(user_id, num_clusters, db):
    global round_num, alpha, beta_values, presented_books, book_embeddings, ids, book_data, cluster_to_books 
    # # embedding_save_path = "data/book_embeddings_openai.json" 
    # ids, book_embeddings = load_embeddings(embedding_save_path)
    # # book_embeddings 정규화 (L2 Norm으로 크기 1로 조정)
    # book_embeddings = normalize(book_embeddings, norm='l2')
    
    book_embeddings = joblib.load("data/book_embeddings.pkl")
    ids = book_embeddings[0]
    
    book_data = get_sentence_from_db(db)

    books = [f"Book {i}" for i in range(len(ids))]  # books는 ids의 길이에 따라 생성
    assert len(books) == len(ids), "Books length mismatch with IDs! "

    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    clusters = kmeans.fit_predict(book_embeddings)

    # 각 클러스터의 책 인덱스 저장
    cluster_to_books = {i: [] for i in range(num_clusters)}
    for idx, cluster_id in enumerate(clusters):
        cluster_to_books[cluster_id].append(idx)

    return ids, book_embeddings, book_data, user_id, cluster_to_books


def suggest_books(question_number, book_embeddings, cluster_to_books, noise_factor, presented_books, suggested_books, books_chosen, book_chosen_dict, book_choice=None):
    if question_number < 30:  # 초반 10 라운드 동안 지수적 감소
        exploration_prob = initial_prob * (decay_factor ** question_number)
    else:  # 이후에는 UCB 기반 조정
        total_selections = len(presented_books)
        exploration_prob = uncertainty_factor / (uncertainty_factor + total_selections)

    if 0 <= question_number <= 4:
        book_a, book_b = get_tournament_winner_cluster_until_round5(book_embeddings, cluster_to_books, presented_books, exploration_prob, 
                                                                    noise_factor, book_choice, question_number, books_chosen, suggested_books)
        return book_a, book_b
    else:
        return 1111, 1112
    

def choice_arrange(user_id, question_number, book_a, book_b, books_chosen, cluster_to_books, book_chosen_dict):
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
        book_choice = update_data(choice, book_a, book_b)

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
        update_data(choice, book_a, book_b)
        return None

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