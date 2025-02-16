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

def neighborhood_based_clustering(weighted_centroid, book_embeddings, num_indices, num_cluster):
    # ✅ 1. 입력 벡터 차원 확인
    assert weighted_centroid.shape[1] == book_embeddings.shape[1], "차원이 일치하지 않습니다."

    # ✅ 2. 코사인 유사도 계산 및 상위 300개 선택
    cosine_similarities = cosine_similarity(book_embeddings, weighted_centroid).flatten()
    
    # ✅ 성능 향상: np.argpartition() 사용
    num_indices = np.argpartition(cosine_similarities, -num_indices)[-num_indices:]
    selected_vectors = book_embeddings[num_indices]

    # ✅ 3. 선택된 벡터 정규화 (코사인 거리 기반 KMeans)
    normalized_vectors = normalize(selected_vectors)

    # ✅ 4. KMeans 클러스터링 (최신 옵션 적용)
    num_clusters = num_cluster
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init='auto')
    clusters = kmeans.fit_predict(normalized_vectors)

    # 각 클러스터의 책 인덱스 저장
    neigh_based_clustering_to_books = {i: [] for i in range(num_clusters)}
    for idx, cluster_id in enumerate(clusters):
        neigh_based_clustering_to_books[cluster_id].append(idx)

    # ✅ 5. 클러스터 결과 출력
    unique, counts = np.unique(clusters, return_counts=True)
    print("K-Means 클러스터 결과:")
    for label, count in zip(unique, counts):
        print(f"클러스터 {label}: {count}개")

    return neigh_based_clustering_to_books, num_indices, kmeans, normalized_vectors

import traceback
import numpy as np

def select_books_for_new_cluster(neigh_based_clustering_to_books, top_300_indices, 
                                weighted_centroid, normalized_vectors, 
                                kmeans, question_number, visited_clusters, 
                                selected_books_of_round678):
    
    # weighted_centroid = np.array(weighted_centroid, copy=True)
    print(f"visited_clusters: {visited_clusters}")
    print(f"All Clusters: {list(neigh_based_clustering_to_books.keys())}")
    print(f"✅ Remaining Clusters: {[c for c in neigh_based_clustering_to_books.keys() if c not in visited_clusters]}")
    print(f"✅ weighted_centroid.shape: {weighted_centroid.shape}")
    
    try:
        print(f"\n🟡 [Start] Selecting books for Question {question_number}")
        print(f"➡️ weighted_centroid.shape: {weighted_centroid.shape}")
        print(f"➡️ normalized_vectors.shape: {normalized_vectors.shape}")
        print(f"➡️ visited_clusters before selection: {visited_clusters}")

        # ✅ 1차 선택: weighted_centroid 기반 (question_number == 5)
        if question_number == 5 or question_number == 8 :
            print("🔹 Step 1: Finding cluster from weighted_centroid")
            centroid_cluster = int(kmeans.predict(weighted_centroid)[0])
            print(f"✅ centroid_cluster from weighted_centroid: {centroid_cluster}")
            
            visited_clusters.add(centroid_cluster)
            print(f"🔹 Step 2: visited_clusters updated: {visited_clusters}")

            if centroid_cluster not in neigh_based_clustering_to_books:
                raise ValueError(f"centroid_cluster {centroid_cluster} not found in cluster_to_books")

            book_a_index = np.random.choice(neigh_based_clustering_to_books[centroid_cluster])
            print(f"✅ book_a_index from centroid cluster: {book_a_index}")
            book_a = int(top_300_indices[book_a_index])

        else:
            # ✅ 2차 및 3차 선택: 가장 큰 미방문 클러스터 기반
            print("🔹 Step 3: Selecting largest unvisited cluster for book_a")
            unvisited_clusters = sorted(
                [(cluster, len(books)) for cluster, books in neigh_based_clustering_to_books.items()
                    if cluster not in visited_clusters],
                key=lambda x: x[1],
                reverse=True
            )
            print(f"📊 Unvisited Clusters (by size): {unvisited_clusters}")

            if unvisited_clusters:
                largest_cluster = unvisited_clusters[0][0]
                visited_clusters.add(largest_cluster)
                print(f"✅ Largest unvisited cluster for book_a: {largest_cluster}")
                
                book_a_index = np.random.choice(neigh_based_clustering_to_books[largest_cluster])
                print(f"✅ book_a_index from largest cluster: {book_a_index}")
                book_a = int(top_300_indices[book_a_index])
            else:
                print("⚠️ No unvisited clusters found for book_a")
                book_a = None

        # ✅ book_b: 다른 미방문 클러스터 중 가장 큰 클러스터
        print("🔹 Step 4: Selecting largest remaining unvisited cluster for book_b")
        remaining_clusters = sorted(
            [(cluster, len(books)) for cluster, books in neigh_based_clustering_to_books.items()
                if cluster not in visited_clusters],
            key=lambda x: x[1],
            reverse=True
        )
        print(f"📊 Remaining Unvisited Clusters: {remaining_clusters}")

        if remaining_clusters:
            largest_cluster = remaining_clusters[0][0]
            visited_clusters.add(largest_cluster)
            print(f"✅ Largest unvisited cluster for book_b: {largest_cluster}")
            
            book_b_index = np.random.choice(neigh_based_clustering_to_books[largest_cluster])
            print(f"✅ book_b_index from largest remaining cluster: {book_b_index}")
            book_b = int(top_300_indices[book_b_index])
        else:
            print("⚠️ No remaining unvisited clusters found for book_b")
            book_b = None

        # ✅ 선택 결과 전역 변수에 기록
        print("🔹 Step 5: Recording selected books")
        selected_books_of_round678.append(book_a)
        selected_books_of_round678.append(book_b)

        # ✅ 최종 결과 출력
        print(f"\n🎯 [선택 완료 - Question {question_number}]")
        print(f"📖 Book A: {book_a}")
        print(f"📖 Book B: {book_b}")
        print(f"✅ Final Visited Clusters: {visited_clusters}\n")

        return book_a, book_b

    except Exception as e:
        print(f"\n❌ Exception occurred during book selection (Question {question_number})")
        traceback.print_exc()  # 상세 스택 트레이스 출력
        raise  # 예외 재발생


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

def load_embeddings(file_path):

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    embeddings = [inner_dict["embedding"] for inner_dict in data.values()]
    ids = np.arange(1, len(embeddings) + 1)
    print("len(ids)!!!!!!!!!!!!!!!!!!!!!!!", len(ids))
    return ids, embeddings


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
