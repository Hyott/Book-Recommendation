import numpy as np
import json
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import beta


def load_book_data(json_file_path):
    """
    JSON 파일에서 책 데이터를 로드합니다.
    """
    with open(json_file_path, 'r', encoding='utf-8') as file:
        book_data = json.load(file)
        book_data = list(book_data.values())
    return book_data

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

# === 로드 및 사용 ===

embedding_save_path = "notebook/book_embeddings.npz"  # 저장된 파일 경로
json_file_path = 'notebook/notebook/data/llm_output[0:1486].json'
# 임베딩 데이터를 로드합니다.
ids, embeddings = load_embeddings(embedding_save_path)
# book data load
book_data = load_book_data(json_file_path)
# 결과 출력
print(f"Loaded {len(ids)} ids.")
print(f"Loaded {len(embeddings)} embeddings.")
print(f"First ID: {ids[0]}")
print(f"First embedding shape: {embeddings[0].shape}")
# print(f"First embedding vector: {embeddings[0]}")


############################################################################

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

# === 데이터 초기화 ===
book_embeddings = embeddings
books = [f"Book {i}" for i in range(len(ids))]
assert len(books) == len(ids), "Books length mismatch with IDs!"
num_books = len(embeddings)

# 초기 클러스터링
num_clusters = 12
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
clusters = kmeans.fit_predict(book_embeddings)
cluster_centers = kmeans.cluster_centers_

# 클러스터와 책 매핑
cluster_to_books = {i: [] for i in range(num_clusters)}
for idx, cluster_id in enumerate(clusters):
    cluster_to_books[cluster_id].append(idx)

# Thompson Sampling 변수 초기화
alpha = np.ones(num_books)
beta_values = np.ones(num_books)
presented_books = set()
selected_clusters = []  # 사용자 선택한 클러스터 기록

# === 함수 정의 ===

def thompson_sampling(alpha, beta_values):
    return np.random.beta(alpha, beta_values)

def select_books(cluster_to_books, alpha, beta_values, presented_books):
    samples = thompson_sampling(alpha, beta_values)
    representative_books = []

    for cluster_id, books_in_cluster in cluster_to_books.items():
        cluster_samples = [(idx, samples[idx]) for idx in books_in_cluster if idx not in presented_books]
        if cluster_samples:
            best_book = max(cluster_samples, key=lambda x: x[1])
            representative_books.append(best_book)

    best_book_a = max(representative_books, key=lambda x: x[1])[0]

    valid_indices = [idx for idx in range(len(samples)) if idx not in presented_books and idx != best_book_a]
    random_book_b = np.random.choice(valid_indices)

    presented_books.add(best_book_a)
    presented_books.add(random_book_b)

    return best_book_a, random_book_b

def update_data(choice, book_a, book_b, alpha, beta_values, clusters, selected_clusters):
    if choice == "a":
        alpha[book_a] += 1
        beta_values[book_b] += 1
        selected_clusters.append(clusters[book_a])
    else:
        alpha[book_b] += 1
        beta_values[book_a] += 1
        selected_clusters.append(clusters[book_b])

def refine_cluster(embeddings, cluster_assignments, target_cluster_id, sub_k):
    target_indices = np.where(cluster_assignments == target_cluster_id)[0]
    target_embeddings = embeddings[target_indices]

    kmeans = KMeans(n_clusters=sub_k, random_state=42)
    sub_clusters = kmeans.fit_predict(target_embeddings)

    refined_clusters = {target_indices[i]: sub_clusters[i] for i in range(len(target_indices))}
    return refined_clusters

# === 메인 루프 ===
total_rounds = 5
for round_num in range(1, total_rounds + 1):
    book_a, book_b = select_books(cluster_to_books, alpha, beta_values, presented_books)
    print(f"\nRound {round_num}: Choose between:")
    print(f"a: Book {book_a}")
    print(f"b: Book {book_b}")

    choice = input("Enter 'a' or 'b': ").strip().lower()
    if choice not in ['a', 'b']:
        print("Invalid choice. Please enter 'a' or 'b'.")
        continue

    update_data(choice, book_a, book_b, alpha, beta_values, clusters, selected_clusters)

# === 5회 반복 후 특정 클러스터 선정 ===
target_cluster_id = max(set(selected_clusters), key=selected_clusters.count)
print(f"\nMost Selected Cluster: {target_cluster_id}")

# === 선택된 클러스터 세분화 ===
sub_k = 5  # 세분화 클러스터 개수
refined_clusters = refine_cluster(book_embeddings, clusters, target_cluster_id, sub_k)
print(f"Refined Cluster Mapping for Cluster {target_cluster_id}: {refined_clusters}")

# === 최종 추천 ===
selected_books = np.array(list(presented_books))
selected_embeddings = book_embeddings[selected_books]
preference_center = selected_embeddings.mean(axis=0).reshape(1, -1)

similarities = cosine_similarity(preference_center, book_embeddings).flatten()
recommended_indices = np.argsort(similarities)[::-1][:10]

print("\nTop 10 Recommended Books:")
for idx in recommended_indices:
    print(f"Book {idx}")














