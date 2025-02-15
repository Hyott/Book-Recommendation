import numpy as np
from numpy.linalg import norm 
import os
print("os.getcwd: ", os.getcwd())
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from psycopg2 import sql
from sqlalchemy.orm import Session
from app.database.models import SentenceTable
import json


def get_choice_bool(cursor, user_id, question_number):
    cursor.execute(
        sql.SQL("SELECT * FROM public.user_responses WHERE user_id = %s and question_number = %s"),
        (user_id, question_number)
    )
    exists = cursor.fetchall()
    if exists:
        book_a_select = exists[0][4]
        book_b_select = exists[1][4]
    else:
        book_a_select = None
        book_b_select = None
    return book_a_select, book_b_select


def get_sentence_from_db(db: Session):
    """
    데이터베이스에서 책 데이터(id, isbn, sentence)만 불러옵니다.
    """
    sentences = db.query(SentenceTable.id, SentenceTable.isbn, SentenceTable.sentence).all()
    
    if not sentences:
        return []

    return [
        {
            "id": sentence.id,
            "isbn": sentence.isbn,
            "sentence": sentence.sentence,
        }
        for sentence in sentences
    ]

# === 임베딩 로드 함수 ===
def load_embeddings(file_path):

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    embeddings = [inner_dict["embedding"] for inner_dict in data.values()]
    ids = np.arange(1, len(embeddings) + 1)
    print("len(ids)!!!!!!!!!!!!!!!!!!!!!!!", len(ids))
    return ids, embeddings

def thompson_sampling(alpha, beta_values):
    """
    Thompson Sampling을 수행하여 각 책의 확률 값을 샘플링.
    """
    return np.random.beta(alpha, beta_values)


def select_books(book_embeddings, cluster_to_books, alpha, beta_values, presented_books, exploration_prob, noise_factor, book_choice):
    """
    클러스터 기반으로 책 쌍 선택.
    - 탐색(Exploration)과 활용(Exploitation)의 균형을 맞춰 책을 선택.
    - 노이즈를 추가하여 선택에 다양성을 부여.
    """

    samples = thompson_sampling(alpha, beta_values)

        # 노이즈 추가
    noise = np.random.normal(0, noise_factor, size=len(samples))
    noisy_samples = samples + noise

    # if book_choice == None:
    if 0.18 < exploration_prob:
    # Thompson Sampling을 통해 각 책의 샘플링 값 계산
        # 클러스터별 대표 책 선택 (확률 값이 높은 책)
        representative_books = []
        # 정수 → 집합(set) 변환
        if isinstance(presented_books, int):
            presented_books = {presented_books}
        # print("type(presented_books): ", type(presented_books))
        # print("presented_books: ", presented_books)

        for cluster_id, books_in_cluster in cluster_to_books.items():
            # print(f"type(books_in_cluster): {type(books_in_cluster)}")
            # print(f"books_in_cluster: {books_in_cluster}")
            cluster_samples = [(idx, noisy_samples[idx]) for idx in books_in_cluster if idx not in presented_books]
            if cluster_samples:
                best_book = max(cluster_samples, key=lambda x: x[1])
                representative_books.append(best_book)

        # 대표 책들 중 가장 높은 샘플링 값을 가진 책 1개 선택
        if not representative_books:
            raise ValueError("No more books to present. All books have been used.")

        best_book_a = max(representative_books, key=lambda x: x[1])[0]

    elif exploration_prob <= 0.18:
    # if book_choice:
        # print(f"book_embeddings shape: {book_embeddings.shape}")
        # print(f"book_embeddings[book_choice] shape: {book_embeddings[book_choice].shape}")
        
        similarities = []
        for idx in range(len(book_embeddings)):
            if idx not in presented_books and idx != book_choice:
                # 벡터를 1D로 변환
                vector_a = book_embeddings[book_choice].reshape(-1)
                vector_b = book_embeddings[idx].reshape(-1)

                # Norm 값 계산
                norm_choice = norm(vector_a)
                norm_idx = norm(vector_b)

                # Norm 값이 0이면 건너뜀
                if norm_choice == 0 or norm_idx == 0:
                    continue

                # 코사인 유사도 계산
                similarity = np.dot(vector_a, vector_b) / (norm_choice * norm_idx)
                similarities.append((idx, similarity))

        # 가장 유사한 책 선택
        if not similarities:
            raise ValueError("No valid books to calculate similarity. Check presented_books and book_choice.")

        best_book_a = max(similarities, key=lambda x: x[1])[0]


    # 탐색 여부 결정
    if 0.18 < exploration_prob :  ## 1~5라운드까지로 한정
        # 탐색: 지금까지 선택된 적이 없는 클러스터 중 하나 선택
        
        unvisited_clusters = [
            cluster_id for cluster_id, books_in_cluster in cluster_to_books.items()
            if any(idx not in presented_books for idx in books_in_cluster)
        ]

        if unvisited_clusters:
            random_cluster = np.random.choice(unvisited_clusters)
            random_book_b = np.random.choice([
                idx for idx in cluster_to_books[random_cluster] if idx not in presented_books and idx != best_book_a
            ])
        else:
            # 모든 클러스터가 방문된 경우, 활용으로 전환
            exploration_prob = 0  # 탐색 비중을 제거하고 활용으로 이동
            
    elif exploration_prob <= 0.18:
        # 활용: 선호도가 높은 책 선택 (노이즈 적용)
        random_book_b = max(
            [(idx, noisy_samples[idx]) for idx in range(len(alpha)) if idx not in presented_books and idx != best_book_a],
            key=lambda x: x[1]
        )[0]
    
    # 중복 방지
    presented_books.add(best_book_a)
    presented_books.add(random_book_b)

    return best_book_a, random_book_b


def get_tournament_winner_cluster_until_round5(book_embeddings, cluster_to_books, alpha, beta_values, 
                                        presented_books, exploration_prob, noise_factor, book_choice, 
                                        question_number, books_chosen, suggested_books):

    if question_number == 0:
        book_a = int(np.random.choice([
            idx for idx in cluster_to_books[0] if idx not in presented_books]))
        
        book_b = int(np.random.choice([
            idx for idx in cluster_to_books[1] if idx not in presented_books]))

    elif question_number == 1:
        book_a = int(np.random.choice([
            idx for idx in cluster_to_books[2] if idx not in presented_books]))
        
        book_b = int(np.random.choice([
            idx for idx in cluster_to_books[3] if idx not in presented_books]))
        
    elif question_number == 2:
        book_a = int(np.random.choice([
            idx for idx in cluster_to_books[4] if idx not in presented_books]))
        
        book_b = int(np.random.choice([
            idx for idx in cluster_to_books[5] if idx not in presented_books]))

    elif question_number == 3:
        winner_of_1 = books_chosen[0]
        cluster_of_winner_1 = None

        for cluster_id, book_list in cluster_to_books.items():
            if winner_of_1 in book_list:
                cluster_of_winner_1 = cluster_id
                break
        print("winner_of_1: ", winner_of_1)
        print("cluster_of_winner_1", cluster_of_winner_1)


        winner_of_2 = books_chosen[1]
        cluster_of_winner_2 = None

        for cluster_id, book_list in cluster_to_books.items():
            if winner_of_2 in book_list:
                cluster_of_winner_2 = cluster_id
                break
        print("winner_of_2: ", winner_of_2)
        print("cluster_of_winner_2", cluster_of_winner_2)

        book_a = int(np.random.choice([
            idx for idx in cluster_to_books[cluster_of_winner_1] if idx not in presented_books]))
        book_b = int(np.random.choice([
            idx for idx in cluster_to_books[cluster_of_winner_2] if idx not in presented_books]))
        
    elif question_number == 4:
        winner_of_3 = books_chosen[2]
        cluster_of_winner_3 = None

        for cluster_id, book_list in cluster_to_books.items():
            if winner_of_3 in book_list:
                cluster_of_winner_3 = cluster_id
                break
        print("winner_of_3: ", winner_of_3)
        print("cluster_of_winner_3", cluster_of_winner_3)

        winner_of_4 = books_chosen[3]
        cluster_of_winner_4 = None

        for cluster_id, book_list in cluster_to_books.items():
            if winner_of_4 in book_list:
                cluster_of_winner_4 = cluster_id
                break
        print("winner_of_4: ", winner_of_4)
        print("cluster_of_winner_4", cluster_of_winner_4)

        book_a = int(np.random.choice([
            idx for idx in cluster_to_books[cluster_of_winner_3] if idx not in presented_books]))
        book_b = int(np.random.choice([
            idx for idx in cluster_to_books[cluster_of_winner_4] if idx not in presented_books]))   

    else:
        raise ValueError("Question number out of range 5")
    


    print("suggested_books : ", suggested_books)
    print("presented_books : ", presented_books)
    print("books_chosen : ", books_chosen)
    presented_books.add(book_a)
    presented_books.add(book_b)
    suggested_books.append(book_a)
    suggested_books.append(book_b) 


    return book_a, book_b



def update_data(choice, book_a, book_b, alpha, beta_values):
    """
    사용자 선택 데이터를 기반으로 베타 분포 업데이트.
    """
    print("book_a:", book_a)
    print("book_b:", book_b)
    if choice == "a":
        alpha[book_a] += 1
        beta_values[book_b] += 1
        # alpha[-1] += 1
        # alpha[0] += 1
        print(book_a)
        return book_a
    elif choice == "b":
        alpha[book_b] += 1
        beta_values[book_a] += 1
        return book_b
    else:
        beta_values[book_a] += 1
        beta_values[book_b] += 1
        return None
        


def get_message_by_id(ids, book_id, book_data):
    """
    ids와 book_data를 이용해 특정 book_id의 메시지를 조회합니다.
    """
    idx = np.where(ids == book_id)[0][0]  # book_id의 인덱스 찾기
    return book_data[idx]["sentence"]


def weighted_sampling(similarities, num_samples=10, temperature=0.5):
    """
    유사도 점수를 기반으로 확률적 샘플링을 수행합니다.
    - similarities: 코사인 유사도 배열
    - num_samples: 추천할 책의 개수
    - temperature: 유사도 가중치 조정을 위한 파라미터 (낮을수록 상위 선택 집중)
    """
    # 유사도를 가중치로 변환
    probabilities = np.exp(similarities / temperature)
    probabilities /= probabilities.sum()  # 확률로 정규화

    # 가중치를 기반으로 랜덤 샘플링
    sampled_indices = np.random.choice(len(similarities), size=num_samples, replace=False, p=probabilities)
    return sampled_indices
