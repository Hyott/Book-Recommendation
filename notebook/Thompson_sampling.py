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



book_embeddings = embeddings
# books = [f"Book {i}" for i in range(len(ids))]
books = [f"Book {i}" for i in range(len(ids))]  # books는 ids의 길이에 따라 생성
assert len(books) == len(ids), "Books length mismatch with IDs!"
num_books = len(embeddings)
# === 클러스터링 ===

# KMeans 클러스터링 (50개의 클러스터로 나눔)
num_clusters = 12
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
clusters = kmeans.fit_predict(book_embeddings)

# 각 클러스터의 책 인덱스 저장
cluster_to_books = {i: [] for i in range(num_clusters)}
for idx, cluster_id in enumerate(clusters):
    cluster_to_books[cluster_id].append(idx)

# 클러스터별 알파, 베타 값 초기화
alpha = np.ones(num_books)
beta_values = np.ones(num_books)

# 이미 제시된 책을 저장할 세트
presented_books = set()

##############################################################################

def thompson_sampling(alpha, beta_values):
    """
    Thompson Sampling을 수행하여 각 책의 확률 값을 샘플링.
    """
    return np.random.beta(alpha, beta_values)


def select_books(cluster_to_books, alpha, beta_values, presented_books, exploration_prob=0.3, noise_factor=0.3):
    """
    클러스터 기반으로 책 쌍 선택.
    - 탐색(Exploration)과 활용(Exploitation)의 균형을 맞춰 책을 선택.
    - 노이즈를 추가하여 선택에 다양성을 부여.
    """
    # Thompson Sampling을 통해 각 책의 샘플링 값 계산
    samples = thompson_sampling(alpha, beta_values)

    # 노이즈 추가
    noise = np.random.normal(0, noise_factor, size=len(samples))
    noisy_samples = samples + noise

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

    # 탐색 여부 결정
    if np.random.rand() < exploration_prob:
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
    else:
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
    else:
        alpha[book_b] += 1
        beta_values[book_a] += 1


def get_message_by_id(ids, book_id, book_data):
    """
    ids와 book_data를 이용해 특정 book_id의 메시지를 조회합니다.
    """
    idx = np.where(ids == book_id)[0][0]  # book_id의 인덱스 찾기
    return book_data[idx]["message"]


########################################################################
    # === 메인 루프 ===

for round_num in range(12):

    # 초기 설정
    initial_prob = 0.3
    decay_factor = 0.9
    uncertainty_factor = 10

    # 탐색 확률 계산
    if round_num < 10:  # 초반 10 라운드 동안 지수적 감소
        exploration_prob = initial_prob * (decay_factor ** round_num)
    else:  # 이후에는 UCB 기반 조정
        total_selections = len(presented_books)
        exploration_prob = uncertainty_factor / (uncertainty_factor + total_selections)
    # 클러스터 기반 책 쌍 선택
    book_a, book_b = select_books(cluster_to_books, alpha, beta_values, presented_books, exploration_prob=exploration_prob)

    # 책 메시지 조회
    message_a = get_message_by_id(ids, ids[book_a], book_data)
    message_b = get_message_by_id(ids, ids[book_b], book_data)

    # 초기 설정
    initial_prob = 0.3
    decay_factor = 0.9
    uncertainty_factor = 10

    # 탐색 확률 계산
    if round_num < 10:  # 초반 10 라운드 동안 지수적 감소
        exploration_prob = initial_prob * (decay_factor ** round_num)
    else:  # 이후에는 UCB 기반 조정
        total_selections = len(presented_books)
        exploration_prob = uncertainty_factor / (uncertainty_factor + total_selections)

    # 사용자에게 책 제시
    print('\n')
    print(f"Round {round_num + 1}: Choose between:")
    print(f"a: {message_a}")
    print(f"b: {message_b}")
    
    # 사용자 입력
    choice = input("Enter 'a' or 'b': ").strip().lower()
    if choice not in ['a', 'b']:
        print("Invalid choice. Please enter 'a' or 'b'.")
        continue

    # 데이터 업데이트
    update_data(choice, book_a, book_b, alpha, beta_values)


####################################################################
    # === 최종 추천 ===

# 사용자 선택 데이터를 기반으로 선호 중심 계산
selected_books = np.array(list(presented_books))
selected_embeddings = book_embeddings[selected_books]
weights = np.arange(1, len(selected_books) + 1)  # 가중치 추가
preference_center = np.average(selected_embeddings, axis=0, weights=weights).reshape(1, -1)

# 중심과 유사한 책 추천 (코사인 유사도 기준)
similarities = cosine_similarity(preference_center, book_embeddings).flatten()

# 유사도에 기반한 확률적 다양성 추가
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

# 가중치 샘플링을 통한 추천
final_recommendations = weighted_sampling(similarities, num_samples=10, temperature=0.7)

# 추천 결과 출력
print("\nTop 10 Recommended Books:")
for idx in final_recommendations:
    # 책 ID를 이용해 메시지 조회
    book_id = ids[idx]
    message = get_message_by_id(ids, book_id, book_data)
    print(f"Book ID: {book_id}")
    print(f"Message: {message}\n")














