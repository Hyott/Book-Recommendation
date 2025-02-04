import numpy as np
from numpy.linalg import norm 
import json
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import beta

import os; print("os.getcwd :", os.getcwd())
from book_rec_module import load_book_data, load_embeddings,select_books, \
    update_data, get_message_by_id, weighted_sampling, get_choice_bool



def first_setting_of_logic(user_id, num_clusters, noise_factor, embedding_save_path, llm_output_path):
    embedding_save_path = "notebook/notebook/data/book_embeddings.npz"  # 저장된 파일 경로
    llm_output_path = 'data/scraping/llm_output_fixed.json'

    ids, book_embeddings = load_embeddings(embedding_save_path)
    book_data = load_book_data(llm_output_path)

    books = [f"Book {i}" for i in range(len(ids))]  # books는 ids의 길이에 따라 생성
    assert len(books) == len(ids), "Books length mismatch with IDs!"
    num_books = len(book_embeddings)

    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    clusters = kmeans.fit_predict(book_embeddings)
    print(clusters.shape)

    # 각 클러스터의 책 인덱스 저장
    cluster_to_books = {i: [] for i in range(num_clusters)}
    for idx, cluster_id in enumerate(clusters):
        cluster_to_books[cluster_id].append(idx)

    alpha = np.ones(num_books)
    beta_values = np.ones(num_books)

    presented_books = set()


    noise_factor = 0.01
    initial_prob = 0.3
    decay_factor = 0.9
    uncertainty_factor = 10
    round_num = 0
    question_number = round_num +1
    return round_num, initial_prob, decay_factor, uncertainty_factor, alpha, beta_values, \
        presented_books, noise_factor, ids, book_data, user_id, question_number, \
        book_embeddings, cluster_to_books


def suggest_books():
    global round_num
    # 탐색 확률 계산
    if round_num < 30:  # 초반 10 라운드 동안 지수적 감소
        exploration_prob = initial_prob * (decay_factor ** round_num)
    else:  # 이후에는 UCB 기반 조정
        total_selections = len(presented_books)
        exploration_prob = uncertainty_factor / (uncertainty_factor + total_selections)

    if round_num == 0:
        book_choice = None
    else:
        book_choice = book_choice_updated

    book_a, book_b = select_books(book_embeddings, cluster_to_books, alpha, 
                                    beta_values, presented_books, exploration_prob, 
                                    noise_factor, book_choice)
    
    # 책 메시지 조회
    message_a = get_message_by_id(ids, ids[book_a], book_data)
    message_b = get_message_by_id(ids, ids[book_b], book_data)

    print('\n')
    print(f"Round {round_num+1}: Choose between:")
    print(f"a: {message_a}")
    print(f"b: {message_b}")

    round_num += 1
    return book_a, book_b


def choice_arrange():
    choice_bool = get_choice_bool(user_id, question_number)
    print(f"{choice_bool = }")

    if choice_bool[0]:
        choice = 'a'
    elif choice_bool[1]:
        choice = 'b'
    else:
        choice = None

    # 데이터 업데이트
    if choice:
        book_choice = update_data(choice, book_a, book_b, alpha, beta_values)
        print('----------Choice----------')
    if not choice:
        update_data(choice, book_a, book_b, alpha, beta_values)
        print("/////// No choice ////////")
    print(f"{book_choice = }")

    return book_choice


def get_recommendations():
    selected_books = np.array(list(presented_books)[-5:])
    selected_embeddings = book_embeddings[selected_books]
    weights = np.arange(1, len(selected_books) + 1)  # 가중치 추가  ######### 다시 볼 필요 있음
    preference_center = np.average(selected_embeddings, axis=0, weights=weights).reshape(1, -1)


    # 중심과 유사한 책 추천 (코사인 유사도 기준)
    similarities = cosine_similarity(preference_center, book_embeddings).flatten()
    final_recommendations = weighted_sampling(similarities, num_samples=10, temperature=0.2)

    return final_recommendations




embedding_save_path = "notebook/notebook/data/book_embeddings.npz"  # 저장된 파일 경로
llm_output_path = 'data/scraping/llm_output_fixed.json'
user_id = 101
num_clusters = 6
noise_factor = 0.01

round_num, initial_prob, decay_factor, uncertainty_factor, alpha, beta_values, \
presented_books, noise_factor, ids, book_data, user_id, question_number, \
book_embeddings, cluster_to_books = first_setting_of_logic(user_id, num_clusters, noise_factor, embedding_save_path, llm_output_path)


book_choice_updated = None


book_a, book_b = suggest_books()

book_choice_updated = choice_arrange()


print(f"{round_num = }")


if round_num == 10:
    final_recommendations = get_recommendations()
    #추천 결과 출력
    print("\nTop 10 Recommended Books:\n")
    for idx in final_recommendations:
        # 책 ID를 이용해 메시지 조회
        book_id = ids[idx]
        message = get_message_by_id(ids, book_id, book_data)
        print(f"Book ID: {book_id}")
        print(f"Message: {message}\n")
