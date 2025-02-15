import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
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

# def get_centroid_after_round5(sorted_cluster_books, book_embeddings, centroid_weight, cluster_of_winner_5):
#     """
#     1위 클러스터의 책 수가 3개인 경우는 2위 개수는 1개이고 3위는 1개이다. -> sorted 는  동률일 경우, 값이 작은 순으로 정렬이므로, 최종연산에서 2위와 3위의 구분이 없을 예정이다.
#     1위 클러스터의 책 수가 2개인 경우, 2위의 개수는 2개이고 3위는 1개이다. -> 2위에 weight를 3위보다 많이 줄 예정이다.
#     """

#     book_values_of_cluster = list(sorted_cluster_books.values())
#     book_keys_of_cluster = list(sorted_cluster_books.keys())
#     print("book_values_of_cluster : ", book_values_of_cluster)
#     print(f"book_keys_of_cluster : {book_keys_of_cluster}")

#     first_cluster_num = cluster_of_winner_5
#     first_cluster_indices = book_values_of_cluster[cluster_of_winner_5]

#     # 🛑 클러스터 추출 로직 수정 (pop 대신 차집합 사용)
#     remaining_clusters = [key for key in book_keys_of_cluster if key != first_cluster_num]

#     if len(book_values_of_cluster[cluster_of_winner_5]) == 3:
#         book_keys_of_cluster.pop(cluster_of_winner_5)
#         print(f"book_keys_of_cluster after pop: {book_keys_of_cluster}")
#         second_cluster_num = book_keys_of_cluster[0]
#         third_cluster_num = book_keys_of_cluster[1]
#         second_cluster_indices = book_values_of_cluster[second_cluster_num]
#         third_cluster_indices = book_values_of_cluster[third_cluster_num]

#         # 2위와 3위 모두 선택된 것은 1번뿐이므로 가중치는 같다
#         weight_first = centroid_weight
#         weight_second = 1 - weight_first * 0.5
#         weight_third = 1 - weight_first * 0.5

#     else:
#         second_cluster_num = book_keys_of_cluster[1]
#         third_cluster_num = book_keys_of_cluster[2]
#         second_cluster_indices = book_values_of_cluster[second_cluster_num]
#         third_cluster_indices = book_values_of_cluster[third_cluster_num]

#         weight_first = centroid_weight
#         weight_second = 1 - weight_first * 0.66
#         weight_third = 1 - weight_first * 0.34
    
#     print(f"first_cluster_num : {first_cluster_num}")
#     print(f"second_cluster_num: {second_cluster_num}")
#     print(f"third_cluster_num: {third_cluster_num}")
    

#     print("type of book_embeddings: ", type(book_embeddings))
#     print("shape of book_embeddings: ", book_embeddings.shape)

#         # 각 클러스터별 벡터 평균 (centroid)
#     centroid_first = np.mean([book_embeddings[idx] for idx in first_cluster_indices], axis=0)
#     centroid_second = np.mean([book_embeddings[idx] for idx in second_cluster_indices], axis=0)
#     centroid_third = np.mean([book_embeddings[idx] for idx in third_cluster_indices], axis=0)

#     # 가중 평균 (Weighted Centroid)
#     weighted_centroid = (centroid_first * weight_first + centroid_second * weight_first + centroid_third * weight_third) / (weight_first + weight_second + weight_third)


#     if isinstance(weighted_centroid, list):
#         weighted_centroid = np.array(weighted_centroid)

# # 2️⃣ 1차원 배열을 2차원 배열로 변환
#     if len(weighted_centroid.shape) == 1:
#         weighted_centroid = weighted_centroid.reshape(1, -1)

#     print("1위 클러스터 중심점:", centroid_first)
#     print("2위 클러스터 중심점:", centroid_second)
#     print("가중 평균 중심점:", weighted_centroid)
#     print(f"shape of weighted_centroid:  {weighted_centroid.shape} ")

#     return weighted_centroid



# import numpy as np

def get_centroid_after_round5(sorted_cluster_books, book_embeddings, centroid_weight, cluster_of_winner_5):
    """
    클러스터 기반 가중 평균 중심점 계산
    """
    # 📌 클러스터 및 책 인덱스 정리
    book_values_of_cluster = list(sorted_cluster_books.values())
    book_keys_of_cluster = list(sorted_cluster_books.keys())

    print("book_values_of_cluster:", book_values_of_cluster)
    print("book_keys_of_cluster:", book_keys_of_cluster)

    first_cluster_num = cluster_of_winner_5
    first_cluster_indices = sorted_cluster_books[first_cluster_num]

    # 🛑 클러스터 추출 로직 수정 (pop 대신 차집합 사용)
    remaining_clusters = [key for key in book_keys_of_cluster if key != first_cluster_num]

    if len(first_cluster_indices) == 3:
        second_cluster_num = remaining_clusters[0]
        third_cluster_num = remaining_clusters[1]

        weight_first = centroid_weight
        weight_second = 0.5 * (1 - weight_first)
        weight_third = 0.5 * (1 - weight_first)

    else:
        second_cluster_num = remaining_clusters[0]
        third_cluster_num = remaining_clusters[1]

        weight_first = centroid_weight
        weight_second = 0.67 * (1 - weight_first)
        weight_third = 0.33 * (1 - weight_first)

    second_cluster_indices = sorted_cluster_books[second_cluster_num]
    third_cluster_indices = sorted_cluster_books[third_cluster_num]

    print(f"first_cluster_num: {first_cluster_num}")
    print(f"second_cluster_num: {second_cluster_num}")
    print(f"third_cluster_num: {third_cluster_num}")
    print(f"weight_first: {weight_first}, weight_second: {weight_second}, weight_third: {weight_third}")
    print(f"first_cluster_indices : {first_cluster_indices}")
    print(f"second_cluster_indices : {second_cluster_indices}")
    print(f"third_cluster_indices : {third_cluster_indices}")


    # ✅ NumPy 슬라이싱 최적화
    centroid_first = np.mean(book_embeddings[first_cluster_indices], axis=0)
    centroid_second = np.mean(book_embeddings[second_cluster_indices], axis=0)
    centroid_third = np.mean(book_embeddings[third_cluster_indices], axis=0)

    # ✅ 가중 평균 계산 수정 (weight_second 사용)
    weighted_centroid = (
        centroid_first * weight_first +
        centroid_second * weight_second +
        centroid_third * weight_third
    ) / (weight_first + weight_second + weight_third)

    # 🛡️ NumPy 배열 변환 및 차원 정리
    if isinstance(weighted_centroid, list):
        weighted_centroid = np.array(weighted_centroid)

    if len(weighted_centroid.shape) == 1:
        weighted_centroid = weighted_centroid.reshape(1, -1)

    print("1위 클러스터 중심점:", centroid_first)
    print("2위 클러스터 중심점:", centroid_second)
    print("3위 클러스터 중심점:", centroid_third)
    print("가중 평균 중심점:", weighted_centroid)
    print(f"shape of weighted_centroid: {weighted_centroid.shape}")

    return weighted_centroid



# import numpy as np

# def get_centroid_after_round5(sorted_cluster_books, book_embeddings, centroid_weight, cluster_of_winner_5):
#     """
#     클러스터 기반 가중 평균 중심점 계산
#     """
#     # 📌 클러스터 및 책 인덱스 정리
#     book_values_of_cluster = list(sorted_cluster_books.values())
#     book_keys_of_cluster = list(sorted_cluster_books.keys())

#     print("📊 book_values_of_cluster:", book_values_of_cluster)
#     print("📊 book_keys_of_cluster:", book_keys_of_cluster)

#     # ✅ 데이터 유효성 검사
#     if not book_values_of_cluster or len(book_values_of_cluster) < 3:
#         print("❌ 클러스터 데이터가 충분하지 않습니다. 기본값 반환.")
#         return np.zeros((1, book_embeddings.shape[1]))

#     # ✅ cluster_of_winner_5 유효성 확인
#     if cluster_of_winner_5 >= len(book_values_of_cluster):
#         print(f"❌ cluster_of_winner_5({cluster_of_winner_5})가 클러스터 범위를 벗어났습니다.")
#         return np.zeros((1, book_embeddings.shape[1]))

#     first_cluster_num = cluster_of_winner_5
#     first_cluster_indices = book_values_of_cluster[first_cluster_num]

#     # ✅ remaining_clusters 계산
#     remaining_clusters = [key for key in book_keys_of_cluster if key != first_cluster_num]

#     # ✅ remaining_clusters 길이 점검
#     if len(remaining_clusters) < 2:
#         print("❌ remaining_clusters의 클러스터 개수가 부족합니다. 기본값 반환.")
#         return np.zeros((1, book_embeddings.shape[1]))

#     if len(first_cluster_indices) == 3:
#         second_cluster_num = remaining_clusters[0]
#         third_cluster_num = remaining_clusters[1]

#         weight_first = centroid_weight
#         weight_second = 1 - weight_first * 0.5
#         weight_third = 1 - weight_first * 0.5
#     else:
#         second_cluster_num = remaining_clusters[0]
#         third_cluster_num = remaining_clusters[1]

#         weight_first = centroid_weight
#         weight_second = 1 - weight_first * 0.66
#         weight_third = 1 - weight_first * 0.34

#     # ✅ second_cluster_indices, third_cluster_indices 유효성 점검
#     if (
#         second_cluster_num >= len(book_values_of_cluster) or 
#         third_cluster_num >= len(book_values_of_cluster)
#     ):
#         print(f"❌ 클러스터 번호({second_cluster_num}, {third_cluster_num})가 유효하지 않습니다. 기본값 반환.")
#         return np.zeros((1, book_embeddings.shape[1]))

#     second_cluster_indices = book_values_of_cluster[second_cluster_num]
#     third_cluster_indices = book_values_of_cluster[third_cluster_num]

#     print(f"first_cluster_num: {first_cluster_num}")
#     print(f"second_cluster_num: {second_cluster_num}")
#     print(f"third_cluster_num: {third_cluster_num}")
#     print(f"weight_first: {weight_first}, weight_second: {weight_second}, weight_third: {weight_third}")

#     # ✅ 클러스터별 평균 벡터 계산
#     if len(first_cluster_indices) == 0 or len(second_cluster_indices) == 0 or len(third_cluster_indices) == 0:
#         print("❌ 일부 클러스터에 책이 없습니다. 기본값 반환.")
#         return np.zeros((1, book_embeddings.shape[1]))

#     centroid_first = np.mean(book_embeddings[first_cluster_indices], axis=0)
#     centroid_second = np.mean(book_embeddings[second_cluster_indices], axis=0)
#     centroid_third = np.mean(book_embeddings[third_cluster_indices], axis=0)

#     # ✅ 가중 평균 계산
#     weighted_centroid = (
#         centroid_first * weight_first +
#         centroid_second * weight_second +
#         centroid_third * weight_third
#     ) / (weight_first + weight_second + weight_third)

#     # 🛡️ NumPy 배열 변환 및 차원 정리
#     if isinstance(weighted_centroid, list):
#         weighted_centroid = np.array(weighted_centroid)

#     if len(weighted_centroid.shape) == 1:
#         weighted_centroid = weighted_centroid.reshape(1, -1)

#     print("✅ 1위 클러스터 중심점:", centroid_first)
#     print("✅ 2위 클러스터 중심점:", centroid_second)
#     print("✅ 3위 클러스터 중심점:", centroid_third)
#     print("✅ 가중 평균 중심점:", weighted_centroid)
#     print(f"✅ shape of weighted_centroid: {weighted_centroid.shape}")

#     return weighted_centroid


def neighborhood_based_clustering(weighted_centroid, book_embeddings):
    # ✅ 1. 입력 벡터 차원 확인
    assert weighted_centroid.shape[1] == book_embeddings.shape[1], "차원이 일치하지 않습니다."

    # ✅ 2. 코사인 유사도 계산 및 상위 300개 선택
    cosine_similarities = cosine_similarity(book_embeddings, weighted_centroid).flatten()
    
    # ✅ 성능 향상: np.argpartition() 사용
    top_300_indices = np.argpartition(cosine_similarities, -300)[-300:]
    selected_vectors = book_embeddings[top_300_indices]

    # ✅ 3. 선택된 벡터 정규화 (코사인 거리 기반 KMeans)
    normalized_vectors = normalize(selected_vectors)

    # ✅ 4. KMeans 클러스터링 (최신 옵션 적용)
    num_clusters = 5
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init='auto')
    clusters = kmeans.fit_predict(normalized_vectors)

    # 각 클러스터의 책 인덱스 저장
    cluster_to_books = {i: [] for i in range(num_clusters)}
    for idx, cluster_id in enumerate(clusters):
        cluster_to_books[cluster_id].append(idx)

    # ✅ 5. 클러스터 결과 출력
    unique, counts = np.unique(clusters, return_counts=True)
    print("K-Means 클러스터 결과:")
    for label, count in zip(unique, counts):
        print(f"클러스터 {label}: {count}개")

    return cluster_to_books, top_300_indices

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
    
    winner_of_q = {f"winner_of_{question_number}"}

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
