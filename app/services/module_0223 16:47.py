import numpy as np
import traceback
from database.crud import get_presented_sentence, get_user_true_response, get_question_number_by_user_id
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity
import joblib

class UserDataStorage:

    def __init__(self):
        self.user_neigh_based_clustering_to_books = defaultdict(lambda: defaultdict(list))
        self.user_books_chosen = defaultdict(lambda: defaultdict(list))  # 클러스터링 데이터
        self.user_visited_clusters = defaultdict(set)
        self.user_weighted_centroid = defaultdict(list)
        self.user_selected_indices_from_weighted_centroid = defaultdict(list)
        self.user_kmeans_2nd = defaultdict(list)
        
    
    def get_user_neigh_based_clustering_to_books(self, user_id):
        return self.user_neigh_based_clustering_to_books[user_id]
    
    def get_user_visited_clusters(self, user_id):
        return self.user_visited_clusters[user_id]
    
    def get_user_books_chosen(self, user_id):
        self.user_books_chosen[user_id] = defaultdict(list)
        return self.user_books_chosen[user_id]
    
    def get_user_weighted_centroid(self, user_id):
        return self.user_weighted_centroid[user_id]
    
    def get_user_selected_indices_from_weighted_centroid(self, user_id):
        return self.user_selected_indices_from_weighted_centroid[user_id]
    
    def get_user_kmeans_2nd(self, user_id):
        # self.user_kmeans_2nd[user_id] = defaultdict(list)
        return self.user_kmeans_2nd[user_id]
    
    



def get_cluster2books(num_clusters, book_embeddings):
    kmeans = KMeans(random_state=42, n_clusters=num_clusters)
    clusters = kmeans.fit_predict(book_embeddings)

    cluster_to_books = {i: [] for i in range(num_clusters)}
    for idx, cluster_id in enumerate(clusters):
        cluster_to_books[cluster_id].append(idx)
        
    return cluster_to_books


user_data_storage = UserDataStorage()

COSINE_SIMILARITY = np.load("data/cosine_similarity.npy")
BOOK_INDICES = np.arange(1, len(COSINE_SIMILARITY) + 1)
BOOK_EMBEDDINGS = normalize(np.load("data/embedding.npy"), norm='l2')
ISBN_ARR = np.load("data/isbn_arr.npy")
CLUSTER_TO_BOOKS = get_cluster2books(6, BOOK_EMBEDDINGS)


class BookRecommendation:
    def __init__(self, user_id, db):
        self.db = db
        self.user_id = user_id
        self.cosine_similarity = COSINE_SIMILARITY
        self.isbn_arr = ISBN_ARR
        self.book_embeddings = BOOK_EMBEDDINGS
        self.book_indices = BOOK_INDICES
        self.cluster_to_books = CLUSTER_TO_BOOKS
        
        self.neigh_based_clustering_to_books = user_data_storage.get_user_neigh_based_clustering_to_books(user_id)
        self.visited_clusters = user_data_storage.get_user_visited_clusters(user_id)
        self.user_books_chosen = user_data_storage.get_user_books_chosen(user_id)
        self.weighted_centroid = user_data_storage.get_user_weighted_centroid(user_id)
        self.selected_indices_from_weighted_centroid = user_data_storage.get_user_selected_indices_from_weighted_centroid(user_id)
        self.kmeans_2nd = user_data_storage.get_user_kmeans_2nd(user_id)

        self.selected_book_indices, self.question_number = get_user_true_response(self.db, user_id)
        self.presented_book_indices = get_presented_sentence(self.db, self.user_id)
        print(f"[DEBUG] question_number : {self.question_number}")


    def get_book_suggestions(self):
        

        if 1 <= self.question_number <= 5:
            print(f"[DEBUG] Running get_tournament_winner_cluster_until_round5() for question_number={self.question_number}")
            suggested_books = self.get_tournament_winner_cluster_until_round5()
            print(f"[DEBUG] Suggested books: {suggested_books}")
            print(f"[DEBUG] Presented books: {self.presented_book_indices}")
            
        elif self.question_number == 6:
            self.weighted_centroid = self.get_centroid_after_round5(centroid_weight=0.7)
            
            
            
            num_2nd_cluster_indices, num_2nd_cluster = 200, 6
            self.neigh_based_clustering_to_books, self.selected_indices_from_weighted_centroid, self.kmeans_2nd = self.neighborhood_based_clustering(num_2nd_cluster_indices, num_2nd_cluster)
            
            user_data_storage.get_user_weighted_centroid(self.user_id).append(self.weighted_centroid)
            user_data_storage.get_user_neigh_based_clustering_to_books(self.user_id).update(self.neigh_based_clustering_to_books)
            user_data_storage.get_user_selected_indices_from_weighted_centroid(self.user_id).append(self.selected_indices_from_weighted_centroid)
            user_data_storage.get_user_kmeans_2nd(self.user_id).append(self.kmeans_2nd)

            suggested_books = self.select_books_for_new_cluster()

        elif 7 <= self.question_number <= 8:
            print("weighted_centroid: ", self.weighted_centroid)
            print("self.kmeans_2nd: ", self.kmeans_2nd)
            suggested_books = self.select_books_for_new_cluster()


        elif 9 <= self.question_number <= 10:
            presented_book_indices = self.presented_book_indices
            book_embeddings = self.book_embeddings

            weights_for_2nd_centroid = np.array([3, 1, 1, 1])  
            vector_of_choice6, vector_of_choice7, vector_of_choice8 = \
                [book_embeddings[presented_book_indices[i]] for i in (5, 6, 7)]
            all_vectors = np.vstack([weights_for_2nd_centroid, vector_of_choice6, vector_of_choice7, vector_of_choice8])
            weighted_centroid_2nd = np.average(all_vectors, axis=0, weights=weights_for_2nd_centroid, keepdims=True)
            print(f"weighted_centroid_2nd : {weighted_centroid_2nd}")

            num_3rd_cluster_indices, num_3rd_cluster = 75, 4
            final_cluster_to_books, top_75_indices, final_kmeans, final_normalized_vectors = self.neighborhood_based_clustering(weights_for_2nd_centroid, 
                                                                                            book_embeddings, num_3rd_cluster_indices, num_3rd_cluster)

        else:
            raise ValueError(f"[ERROR] No books suggested for question_number={self.question_number}")
        
        return suggested_books, self.question_number


    

    

    def get_tournament_winner_cluster_until_round5(self):
        cluster_to_books = self.cluster_to_books
        presented_book_indices = self.presented_book_indices
        question_number = self.question_number
        selected_book_indices = self.selected_book_indices
        print(f"selected_book_indices : {selected_book_indices}")
        
        if question_number == 1:
            book_a = int(np.random.choice([
                idx for idx in cluster_to_books[0] if idx not in presented_book_indices]))

            book_b = int(np.random.choice([
                idx for idx in cluster_to_books[1] if idx not in presented_book_indices]))

        elif question_number == 2:
            book_a = int(np.random.choice([
                idx for idx in cluster_to_books[2] if idx not in presented_book_indices]))
            
            book_b = int(np.random.choice([
                idx for idx in cluster_to_books[3] if idx not in presented_book_indices]))
            
        elif question_number == 3:
            book_a = int(np.random.choice([
                idx for idx in cluster_to_books[4] if idx not in presented_book_indices]))
            
            book_b = int(np.random.choice([
                idx for idx in cluster_to_books[5] if idx not in presented_book_indices]))

        elif question_number == 4:
            if not selected_book_indices:
                raise ValueError("selected_book_indices가 비어 있음")
            winner_of_1 = selected_book_indices[0]
            cluster_of_winner_1 = None

            for cluster_id, book_list in cluster_to_books.items():
                if winner_of_1 in book_list:
                    cluster_of_winner_1 = cluster_id
                    break
            print("winner_of_1: ", winner_of_1)
            print("cluster_of_winner_1", cluster_of_winner_1)


            winner_of_2 = selected_book_indices[1]
            cluster_of_winner_2 = None

            for cluster_id, book_list in cluster_to_books.items():
                if winner_of_2 in book_list:
                    cluster_of_winner_2 = cluster_id
                    break
            print("winner_of_2: ", winner_of_2)
            print("cluster_of_winner_2", cluster_of_winner_2)

            book_a = int(np.random.choice([
                idx for idx in cluster_to_books[cluster_of_winner_1] if idx not in presented_book_indices]))
            book_b = int(np.random.choice([
                idx for idx in cluster_to_books[cluster_of_winner_2] if idx not in presented_book_indices]))
            
        elif question_number == 5:

            if not selected_book_indices:
                raise ValueError("selected_book_indices가 비어 있음")
            winner_of_3 = selected_book_indices[2]
            cluster_of_winner_3 = None

            for cluster_id, book_list in cluster_to_books.items():
                if winner_of_3 in book_list:
                    cluster_of_winner_3 = cluster_id
                    break
            print("winner_of_3: ", winner_of_3)
            print("cluster_of_winner_3", cluster_of_winner_3)

            winner_of_4 = selected_book_indices[3]
            cluster_of_winner_4 = None

            for cluster_id, book_list in cluster_to_books.items():
                if winner_of_4 in book_list:
                    cluster_of_winner_4 = cluster_id
                    break
            print("winner_of_4: ", winner_of_4)
            print("cluster_of_winner_4", cluster_of_winner_4)

            book_a = int(np.random.choice([
                idx for idx in cluster_to_books[cluster_of_winner_3] if idx not in presented_book_indices]))
            book_b = int(np.random.choice([
                idx for idx in cluster_to_books[cluster_of_winner_4] if idx not in presented_book_indices]))

        else:
            raise ValueError("Question number out of range 5")

        suggested_books = list(map(int, [book_a, book_b]))
        # return book_a, book_b
        return suggested_books
        
    def final_selection(self):
        pass


    def books_chosen_dict_update(self):
        books_chosen_dict = self.user_books_chosen

        for selected_book in self.selected_book_indices:
            cluster_of_choice = None
            for cluster_id, book_list in self.cluster_to_books.items():
                if selected_book in book_list:
                    cluster_of_choice = cluster_id
                    break

            books_chosen_dict[cluster_of_choice].append(selected_book)
        print("books_chosen_dict: ", books_chosen_dict)
        return books_chosen_dict
        

    def get_centroid_after_round5(self, centroid_weight=0.7):
        
        book_embeddings = self.book_embeddings
        books_chosen_dict = self.books_chosen_dict_update()
        sorted_items = sorted(books_chosen_dict.items(), 
                                    key=lambda x: (len(x[1]), -x[0]), reverse=True) # 리스트 길이를 기준으로 정렬 (길이가 같으면 키가 작은 순서)
        
        sorted_cluster_books = dict(sorted_items)

        book_values_of_cluster = list(sorted_cluster_books.values())
        book_keys_of_cluster = list(sorted_cluster_books.keys())

        # print("book_values_of_cluster:", book_values_of_cluster)
        # print("book_keys_of_cluster:", book_keys_of_cluster)

        winner_of_5 = self.selected_book_indices[4]
        cluster_of_winner_5 = None
        for cluster_id, book_list in self.cluster_to_books.items():
            if winner_of_5 in book_list:
                cluster_of_winner_5 = cluster_id
                break

        first_cluster_num = cluster_of_winner_5
        first_cluster_indices = sorted_cluster_books[first_cluster_num]
        remaining_clusters = [key for key in book_keys_of_cluster if key != first_cluster_num]

        #1위 클러스터 길이의 경우의 수는 3, 2 둘 뿐이다ㅏ.
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

        # NumPy 슬라이싱 최적화
        centroid_first = np.mean(book_embeddings[first_cluster_indices], axis=0)
        centroid_second = np.mean(book_embeddings[second_cluster_indices], axis=0)
        centroid_third = np.mean(book_embeddings[third_cluster_indices], axis=0)

        weighted_centroid = (
        centroid_first * weight_first +
        centroid_second * weight_second +
        centroid_third * weight_third
         ) / (weight_first + weight_second + weight_third)
        
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


    def neighborhood_based_clustering(self, num_indices, num_clusters):
        # ✅ 1. 입력 벡터 차원 확인
        assert self.weighted_centroid.shape[1] == self.book_embeddings.shape[1], "차원이 일치하지 않습니다."

        # ✅ 2. cluster_of_winner_5를 제외한 벡터 인덱스 선택
        # all_indices = np.arange(self.book_embeddings.shape[0])  # 전체 벡터 인덱스
        
        cluster_of_winner_5 = self.cluster_to_books.get(5, [])  # 클러스터 5번의 모든 벡터 가져오기
        valid_indices = np.setdiff1d(self.book_indices, cluster_of_winner_5) - 1  # ❌ 클러스터 5번 제거

        # ✅ 3. 코사인 유사도 계산 (cluster_of_winner_5 제외한 벡터들만) : 벡터 그 자체 반환
        cosine_similarities = cosine_similarity(self.book_embeddings[valid_indices], self.weighted_centroid).flatten()

        print("cosine_similarities : ", cosine_similarities)
        # ✅ 4. weighted_centroid와 가장 가까운 200개 벡터 선택
        selected_relative_indices = np.argpartition(cosine_similarities, -num_indices)[-num_indices:]
        selected_new_indices = valid_indices[selected_relative_indices]  # ✅ 원래 인덱스로 변환

        # ✅ 최종 선택된 벡터 결합 (cluster_of_winner_5 추가)
        selected_indices_from_weighted_centroid = np.unique(np.concatenate([selected_new_indices, cluster_of_winner_5]))

        # ✅ 최종 선택된 벡터 개수 출력
        print(f"[INFO] weighted_centroid 기반 {num_indices}개 (클러스터 5번 제외)")
        print(f"[INFO] cluster_of_winner_5 개수: {len(cluster_of_winner_5)}개")
        print(f"[INFO] 최종 선택된 벡터 개수 (중복 제거): {len(self.selected_indices_from_weighted_centroid)}개")

        # ✅ 선택된 벡터 가져오기
        selected_vectors = self.book_embeddings[selected_indices_from_weighted_centroid]

        # 1D 배열인 경우 2D 배열로 변환
        if selected_vectors.ndim == 1:
            selected_vectors = selected_vectors.reshape(1, -1)

        # ✅ 5. KMeans 클러스터링 (최신 옵션 적용)
        kmeans_2nd = KMeans(n_clusters=num_clusters, random_state=42, n_init='auto')
        clusters = kmeans_2nd.fit_predict(selected_vectors)

        # ✅ 6. 각 클러스터의 책 인덱스 저장
        neigh_based_clustering_to_books = {i: [] for i in range(num_clusters)}
        for idx, cluster_id in enumerate(clusters):
            neigh_based_clustering_to_books[cluster_id].append(int(selected_indices_from_weighted_centroid[idx]))
            

        # ✅ 7. 클러스터 결과 출력
        unique, counts = np.unique(clusters, return_counts=True)
        print("K-Means 클러스터 결과:")
        for label, count in zip(unique, counts):
            print(f"클러스터 {label}: {count}개")
        print(f"kmeans_2nd : {kmeans_2nd}")


        return neigh_based_clustering_to_books, selected_indices_from_weighted_centroid, kmeans_2nd


    def select_books_for_new_cluster(self):
        
        presented_book_indices = self.presented_book_indices
        neigh_based_clustering_to_books = self.neigh_based_clustering_to_books
        weighted_centroid = self.weighted_centroid
        visited_clusters = self.visited_clusters
        question_number = self.question_number
        if isinstance(self.kmeans_2nd, list):
            self.kmeans_2nd = self.kmeans_2nd[0]
        kmeans_2nd = self.kmeans_2nd
        selected_indices_from_weighted_centroid = self.selected_indices_from_weighted_centroid
        print(f"presented_book_indices: {presented_book_indices}")

        # print(f"visited_clusters: {visited_clusters}")
        # print(f"All Clusters: {list(neigh_based_clustering_to_books.keys())}")
        # print(f"✅ Remaining Clusters: {[c for c in neigh_based_clustering_to_books.keys() if c not in visited_clusters]}")
        # print(f"✅ weighted_centroid len: {len(weighted_centroid)}")
        
        try:
            print(f"\n🟡 [Start] Selecting books for Question {self.question_number}")
            print(f"➡️ weighted_centroid len: {len(weighted_centroid)}")
            print(f"➡️ visited_clusters before selection: {visited_clusters}")

            # ✅ 1차 선택: weighted_centroid 기반 (question_number == 5)
            if question_number == 6 or question_number == 9 :
                print("🔹 Step 1: Finding cluster from weighted_centroid")
                centroid_cluster = int(kmeans_2nd.predict(weighted_centroid)[0])
                print(f"✅ centroid_cluster from weighted_centroid: {centroid_cluster}")
                
                visited_clusters.add(centroid_cluster)
                print(f"🔹 Step 2: visited_clusters updated: {visited_clusters}")
                if centroid_cluster not in neigh_based_clustering_to_books.keys():
                    raise ValueError(f"centroid_cluster {centroid_cluster} not found in cluster_to_books")
                
                # print(f"selected_indices_from_weighted_centroid:  {selected_indices_from_weighted_centroid}")
                # print(f"neigh_based_clustering_to_books:  {neigh_based_clustering_to_books}")
                
                available_books = [idx for idx in neigh_based_clustering_to_books[centroid_cluster] 
                                if idx not in presented_book_indices]
                print(f"Type of presented_book_indices elements: {[type(x) for x in presented_book_indices]}")
                print(f"Type of available_books elements: {[type(x) for x in available_books]}")
                # [수정된 중복 검증 로직]
                intersection_a = set(available_books).intersection(presented_book_indices)
                print(f"🔍 [DEBUG] Intersection with presented_book_indices for book_a: {intersection_a}")

                if not available_books:
                    raise ValueError(f"No available books in centroid cluster {centroid_cluster} excluding presented ones.")

                book_a = int(np.random.choice(available_books))

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
                    try:
                        largest_cluster = unvisited_clusters[0][0]
                    except IndexError:
                        print("[INFO] 방문할 수 있는 클러스터가 없습니다.")

                    visited_clusters.add(largest_cluster)
                    print(f"✅ Largest unvisited cluster for book_a: {largest_cluster}")

                    # 중복 없는 후보군 필터링
                    available_books = [idx for idx in neigh_based_clustering_to_books[largest_cluster] 
                                    if idx not in presented_book_indices]
                    intersection_a = set(available_books).intersection(presented_book_indices)
                    # print(f"🔍 [DEBUG] Intersection with presented_book_indices for book_a: {intersection_a}")
                    if not available_books:
                        raise ValueError(f"No available books in centroid cluster {largest_cluster} excluding presented ones.")
                    
                    book_a = int(np.random.choice(available_books))

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


                available_books_for_b = [idx for idx in neigh_based_clustering_to_books[largest_cluster] 
                                    if idx not in presented_book_indices]
                intersection_b = set(available_books_for_b).intersection(presented_book_indices)
                # print(f"🔍 [DEBUG] Intersection with presented_book_indices for book_b: {intersection_b}")
                if not available_books_for_b:
                    raise ValueError(f"No available books in centroid cluster {largest_cluster} excluding presented ones.")
                
                book_b = int(np.random.choice(available_books_for_b))
                
            else:
                print("⚠️ No remaining unvisited clusters found for book_b")
                book_b = None

            # ✅ 최종 결과 출력
            print(f"\n🎯 [선택 완료 - Question {question_number}]")
            print(f"📖 Book A: {book_a}")
            print(f"📖 Book B: {book_b}")
            print(f"✅ Final Visited Clusters: {visited_clusters}\n")

            suggested_books = [book_a, book_b]
            print(f"suggested_books: {suggested_books}")
            return suggested_books

        except Exception as e:
            print(f"\n❌ Exception occurred during book selection (Question {question_number})")
            traceback.print_exc()  # 상세 스택 트레이스 출력
            raise  # 예외 재발생




