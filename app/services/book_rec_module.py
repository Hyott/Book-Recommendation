import numpy as np
from numpy.linalg import norm 
import json
import os
print("os.getcwd: ", os.getcwd())
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.database.connection import database_engine
import psycopg2
from psycopg2 import sql

from sqlalchemy.orm import Session
from app.database.models import SentenceTable




# 데이터베이스 연결 설정
host = "localhost"
port = 5432
user = "postgres"
password = "2345"
database_name = "book_recommend"

engine = database_engine(host, port, user, password, database_name)


conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname="book_recommend"
        )
conn.autocommit = True
cursor = conn.cursor()


def get_choice_bool(user_id, question_number):
    cursor.execute(
        sql.SQL("SELECT * FROM public.user_responses WHERE user_id = %s and question_number = %s"),
        (user_id, question_number)
    )
    exists = cursor.fetchall()
    book_a_select = exists[0][4]
    book_b_select = exists[1][4]

    return book_a_select, book_b_select


def get_sentences_from_db(db: Session):
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

# def load_book_data(json_file_path):
#     """
#     JSON 파일에서 책 데이터를 로드합니다.
#     """
#     with open(json_file_path, 'r', encoding='utf-8') as file:
#         book_data = json.load(file)
#         book_data = list(book_data.values())
#     return book_data


# === 임베딩 로드 함수 ===
def load_embeddings(file_path):
    """
    npz 파일에서 저장된 임베딩과 관련 데이터를 로드합니다.
    """
    # 저장된 데이터를 불러옴
    data = np.load(file_path, allow_pickle=True)
    ids = data['ids']  # ISBN 또는 기타 ID
    embeddings = data['embeddings']  # 임베딩 벡터
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
        for cluster_id, books_in_cluster in cluster_to_books.items():
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


def update_data(choice, book_a, book_b, alpha, beta_values):
    """
    사용자 선택 데이터를 기반으로 베타 분포 업데이트.
    """
    if choice == "a":
        alpha[book_a] += 1
        beta_values[book_b] += 1
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
