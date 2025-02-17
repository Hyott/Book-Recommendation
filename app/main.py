from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
import psycopg2
from database.crud import get_book_by_isbn, get_sentence_by_isbn, add_user_response, get_tags_by_isbn, get_question_number_by_user_id
from database.schemas import BookSchema, SentenceSchema, UserResponseSchema, ImageResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from services.book_rec_module import load_embeddings, \
    update_data, get_message_by_id, get_choice_bool, \
        get_sentence_from_db, get_tournament_winner_cluster_until_round5, \
        get_centroid_after_round5, neighborhood_based_clustering, select_books_for_new_cluster
from dotenv import load_dotenv
import os
from app.database.connection import database_engine
from fastapi.responses import JSONResponse
from collections import defaultdict
from fastapi.staticfiles import StaticFiles
import time
from sklearn.preprocessing import normalize
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
user_book_chosen_dict = defaultdict(lambda: defaultdict(list))
user_sorted_cluster_books = defaultdict(lambda: defaultdict(list)) 
user_weighted_centroid = defaultdict(list)
user_weighted_centroid_2nd = defaultdict(list)
user_cluster_to_books = defaultdict(lambda: defaultdict(list))
user_neigh_based_clustering_to_books = defaultdict(lambda: defaultdict(list))
user_visited_clusters = defaultdict(set)
user_final_visited_clusters = defaultdict(set)
user_selected_books_of_round678 = defaultdict(list)
user_selected_books_of_round910 = defaultdict(list)
user_final_cluster_to_books = defaultdict(lambda: defaultdict(list))

user_book_a = defaultdict(int)
user_book_b = defaultdict(int)


embedding_save_path = "data/book_embeddings_openai.json" 
book_data = None
num_clusters = 6
user_id = None
question_number = 0
cluster_to_books = None
top_300_indices = None
normalized_vectors = None
kmeans = None

final_normalized_vectors = None
final_kmeans = None
top_75_indices = None


initial_prob = 0.3
decay_factor = 0.9
uncertainty_factor = 10
noise_factor = 0.01
centroid_weight = 0.6

@app.get("/recommendation/{user_id}")
def get_book_suggestions(user_id: str, db: Session = Depends(get_db)):
    ####### None 출력 대비 5회 시도 설정
    MAX_ATTEMPTS = 5
    for attempt in range(MAX_ATTEMPTS): 
        global user_cluster_to_books, neigh_based_clustering_to_books, book_embeddings, \
            book_data, ids, book_a, book_b, centroid_weight, \
            exploration_prob, book_choice, user_presented_books, \
            user_suggested_books, user_books_chosen, \
            user_book_chosen_dict, user_weighted_centroid,\
            user_visited_clusters, top_300_indices, normalized_vectors, kmeans,\
            user_neigh_based_clustering_to_books, user_final_cluster_to_books,\
            user_final_visited_clusters, user_selected_books_of_round910, user_weighted_centroid_2nd,\
            top_75_indices, final_normalized_vectors, final_kmeans, book_a, book_b
        
        question_number = get_question_number_by_user_id(db, user_id)
        print('question_number:!!!!!!!!!!!!!!!!!!!!!!!!!!!!', question_number)
        
        if user_id not in user_presented_books:
            print(f"New user detected: {user_id}. Initializing presented_books, cluster_to_books and embeddings...")  
            
            ids, book_embeddings, book_data, user_id, first_cluster_to_books = first_setting_of_logic(
                user_id, num_clusters, embedding_save_path, db)  
            
            user_cluster_to_books[user_id] = first_cluster_to_books
            print(f"✅ user_cluster_to_books[{user_id}]에 클러스터 저장 완료.")


        presented_books = user_presented_books[user_id]
        suggested_books = user_suggested_books[user_id]
        books_chosen = user_books_chosen[user_id]
        book_chosen_dict = user_book_chosen_dict[user_id]
        sorted_cluster_books = user_sorted_cluster_books[user_id]
        weighted_centroid = user_weighted_centroid[user_id]
        cluster_to_books = user_cluster_to_books[user_id]
        visited_clusters = user_visited_clusters[user_id]
        final_visited_clusters = user_final_visited_clusters[user_id]
        selected_books_of_round678 = user_selected_books_of_round678[user_id]
        selected_books_of_round910 = user_selected_books_of_round910[user_id]
        neigh_based_clustering_to_books = user_neigh_based_clustering_to_books[user_id]
        final_cluster_to_books = user_final_cluster_to_books[user_id]
        weighted_centroid_2nd = user_weighted_centroid_2nd[user_id]
        

        book_a_isbn = None
        book_b_isbn = None
        message_a = None
        message_b = None

        if question_number == 0:
            book_a, book_b = suggest_books(question_number, book_embeddings, 
                                            cluster_to_books, noise_factor, presented_books, 
                                            suggested_books, books_chosen, book_chosen_dict)
            print("This is 'if' :", book_a, book_b)

        elif 1 <= question_number <= 4:
            print("This is 'elif' - first :", book_a, book_b)
            book_choice_updated = choice_arrange(user_id, question_number, book_a, book_b, 
                                                books_chosen, cluster_to_books, 
                                                book_chosen_dict)
            print("book_choice_updated : ", book_choice_updated)
            book_a, book_b = suggest_books(question_number, book_embeddings, cluster_to_books, 
                                            noise_factor, presented_books, suggested_books, 
                                            books_chosen, book_chosen_dict, book_choice_updated)
            print("This is 'elif' -second :", book_a, book_b)

        
        elif question_number == 5:
            time.sleep(1)
            print("This is 'elif' - first :", book_a, book_b)
            book_choice_updated = choice_arrange(user_id, question_number, book_a, book_b, 
                                                books_chosen, cluster_to_books, book_chosen_dict)
            print("book_choice_updated : ", book_choice_updated)
            # 가장 많이 선택된 {클러스터 번호 : 책 인덱스} 반환
            sorted_items = sorted(book_chosen_dict.items(), 
                                    key=lambda x: (len(x[1]), -x[0]), reverse=True) # 리스트 길이를 기준으로 정렬 (길이가 같으면 키가 작은 순서)
            sorted_cluster_books = dict(sorted_items)
            
            
            print("sorted_cluster_books : ", sorted_cluster_books)
            
            winner_of_5 = books_chosen[4]
            cluster_of_winner_5 = None

            for cluster_id, book_list in cluster_to_books.items():
                if winner_of_5 in book_list:
                    cluster_of_winner_5 = cluster_id
                    break

            weighted_centroid = get_centroid_after_round5(sorted_cluster_books, 
                                book_embeddings, centroid_weight, cluster_of_winner_5)
            
            print(f"user_weighted_centroid: {weighted_centroid}")
            print(f"type user_weighted_centroid : {type(weighted_centroid)}")


            num_2nd_cluster_indices, num_2nd_cluster = 300, 6
            neigh_based_clustering_to_books, top_300_indices, kmeans, normalized_vectors = neighborhood_based_clustering(weighted_centroid, book_embeddings, num_2nd_cluster_indices, num_2nd_cluster)
            print("neigh_based_clustering_to_books :", neigh_based_clustering_to_books)
            print(f"top_300_indices : {top_300_indices}")

            #6번라운드에 제안될 책 추출
            book_a, book_b = select_books_for_new_cluster(presented_books, neigh_based_clustering_to_books, top_300_indices, 
                                                        weighted_centroid, normalized_vectors, 
                                                        kmeans, question_number, visited_clusters, 
                                                        selected_books_of_round678)
            print(f"selected_books_of_round678 : {selected_books_of_round678}")
            presented_books.add(book_a) ; presented_books.add(book_b)
            suggested_books.append(book_a) ; suggested_books.append(book_b)

            # ✅ 사용자별 전역 딕셔너리에 업데이트 추가
            user_weighted_centroid[user_id] = weighted_centroid
            user_neigh_based_clustering_to_books[user_id] = neigh_based_clustering_to_books
            ### 아래 3 변수는 직접 업데이트를 하지 않아도 전체 코드가 잘 돌아감. 그래서 주석처리.
            # user_top_300_indices[user_id] = top_300_indices
            # user_kmeans[user_id] = kmeans
            # user_normalized_vectors[user_id] = normalized_vectors
            
            # 📌 디버깅 로그
            print(f"✅ user_weighted_centroid[{user_id}] 저장 완료")
            print(f"✅ user_neigh_based_clustering_to_books[{user_id}] 저장 완료")
        
        
        elif 6 <= question_number <= 7 :

            book_choice_updated = choice_arrange(user_id, question_number, book_a, book_b, 
                                                books_chosen, cluster_to_books, book_chosen_dict)
            print("book_choice_updated : ", book_choice_updated)
            book_a, book_b = select_books_for_new_cluster(presented_books, neigh_based_clustering_to_books, top_300_indices, 
                                                        weighted_centroid, normalized_vectors, 
                                                        kmeans, question_number, visited_clusters, 
                                                        selected_books_of_round678)
            print(f"selected_books_of_round678 : {selected_books_of_round678}")
            presented_books.add(book_a) ; presented_books.add(book_b)
            suggested_books.append(book_a) ; suggested_books.append(book_b)
        

        elif question_number == 8: 
            time.sleep(1)  
            book_choice_updated = choice_arrange(user_id, question_number, book_a, book_b, 
                                            books_chosen, cluster_to_books, book_chosen_dict)
            print("book_choice_updated : ", book_choice_updated)
            

            weights_for_2nd_centroid = np.array([3, 1, 1, 1])  
            vector_of_choice6 = book_embeddings[books_chosen[5]]
            vector_of_choice7 = book_embeddings[books_chosen[6]]
            vector_of_choice8 = book_embeddings[books_chosen[7]]
            all_vectors = np.vstack([weighted_centroid, vector_of_choice6, vector_of_choice7, vector_of_choice8])
            # 가중 평균으로 new_centroid 계산
            weighted_centroid_2nd = np.average(all_vectors, axis=0, weights=weights_for_2nd_centroid, keepdims=True)
            print(f"weighted_centroid_2nd : {weighted_centroid_2nd}")

            # final clustering
            num_3rd_cluster_indices, num_3rd_cluster = 75, 4
            final_cluster_to_books, top_75_indices, final_kmeans, final_normalized_vectors = neighborhood_based_clustering(weighted_centroid, 
                                                                                            book_embeddings, num_3rd_cluster_indices, num_3rd_cluster)
            user_weighted_centroid_2nd[user_id] = weighted_centroid_2nd
            user_final_cluster_to_books[user_id] = final_cluster_to_books


            book_a, book_b = select_books_for_new_cluster(presented_books, final_cluster_to_books, top_75_indices, 
                                                        weighted_centroid_2nd, final_normalized_vectors, 
                                                        final_kmeans, question_number, final_visited_clusters, 
                                                        selected_books_of_round910)
            print(f"selected_books_of_round910 : {selected_books_of_round910}")
            presented_books.add(book_a) ; presented_books.add(book_b)
            suggested_books.append(book_a) ; suggested_books.append(book_b)


        elif question_number == 9:
            book_choice_updated = choice_arrange(user_id, question_number, book_a, book_b, 
                                            books_chosen, cluster_to_books, book_chosen_dict)
            print("book_choice_updated : ", book_choice_updated)

            book_a, book_b = select_books_for_new_cluster(presented_books, final_cluster_to_books, top_75_indices, 
                                                        weighted_centroid_2nd, final_normalized_vectors, 
                                                        final_kmeans, question_number, final_visited_clusters, 
                                                        selected_books_of_round910)
            print(f"selected_books_of_round910 : {selected_books_of_round910}")
            presented_books.add(book_a) ; presented_books.add(book_b)
            suggested_books.append(book_a) ; suggested_books.append(book_b)
            print(f"presented_books : {presented_books}")

        else:
            raise ValueError("올바르지 않은 question_number가 입력되었습니다.")

        # ISBN + 문장을 함께 반환
        if book_a is not None and book_b is not None:
            question_number += 1
            book_a_isbn = get_isbn_by_id(ids, ids[book_a], book_data)
            book_b_isbn = get_isbn_by_id(ids, ids[book_b], book_data)

            message_a = get_message_by_id(ids, ids[book_a], book_data)
            message_b = get_message_by_id(ids, ids[book_b], book_data)
            user_book_a[user_id] = book_a
            user_book_b[user_id] = book_b

            print('\n')
            print(f"Round {question_number}: Choose between:")
            print(f"a: {message_a}")
            print(f"b: {message_b}")
            print('\n')

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
    
    raise ValueError(f"📌 책 추천 실패: {MAX_ATTEMPTS}회 시도 후에도 추천되지 않았습니다.")



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


def first_setting_of_logic(user_id, num_clusters, embedding_save_path, db):
    global round_num, presented_books, book_embeddings, ids, book_data, cluster_to_books 
    # embedding_save_path = "data/book_embeddings_openai.json" 

    ids, book_embeddings = load_embeddings(embedding_save_path)

    # book_embeddings 정규화 (L2 Norm으로 크기 1로 조정)
    book_embeddings = normalize(book_embeddings, norm='l2')

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

@app.get("/get-image/{image_name}", response_model=ImageResponse)
async def get_image(image_name: str):
    base_url = "https://fromsentence.com/images/"  # 실제 이미지가 호스팅된 URL
    return {"image_url": f"{base_url}{image_name}"}

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

    response_data = {
        "isbn": book.isbn,
        "title": book.title,
        "author": book.author,
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
