import numpy as np
from database.crud import get_user_select_sentence, get_user_true_response
import joblib

# 전역 변수로 데이터 로드 (모듈 최상단에 위치)
COSINE_SIMILARITY = np.load("data/cosine_similarity.npy")
EMBEDDING = np.load("data/embedding.npy")
ISBN_ARR = np.load("data/isbn_arr.npy")
KMEANS_MODEL = joblib.load('data/kmeans_model.pkl')

class RecommendationEngine:
  def __init__(self, db):
    # 전역 변수 사용
    self.cosine_similarity = COSINE_SIMILARITY
    self.embedding = EMBEDDING
    self.isbn_arr = ISBN_ARR
    self.kmeans_model = KMEANS_MODEL
    self.book_indices = np.arange(1, len(self.cosine_similarity) + 1)
    self.db = db
    
  def to_zero_index(self, indices):
    # 1-indexed 리스트나 배열을 0-indexed로 변환
    return np.array(indices) - 1

  def to_one_index(self, indices):
      # 0-indexed 리스트나 배열을 1-indexed로 변환
      return np.array(indices) + 1
    
  def get_book_options(self, user_id):
    selected_book_indices, question_number = get_user_true_response(self.db, user_id)
    selected_all_indices = get_user_select_sentence(self.db, user_id)
    if selected_book_indices:
        # 1-indexed 값을 0-indexed로 변환해서 cosine_similarity 접근
        selected_zero_indices = self.to_zero_index(selected_book_indices)
        average_similarity = self.cosine_similarity[selected_zero_indices, :].mean(axis=0)  # 열 방향 평균

        ranked_indices = self.to_one_index(np.argsort(-average_similarity))  # 이 값은 0-index 기준
        remove_selected_indices = ranked_indices[~np.isin(ranked_indices, selected_all_indices)]
        book_a = np.random.choice(remove_selected_indices[10:len(self.book_indices)//3], 1)
        book_b = np.random.choice(remove_selected_indices[-len(self.book_indices)//3:-100], 1)

        recommended_books = list(map(int, [book_a, book_b]))
        return recommended_books, question_number
    else:
        # self.book_indices는 이미 1-indexed이므로 그대로 사용
        return list(map(int, np.random.choice(self.book_indices, 2))), question_number

  
  def get_result_isbn(self, user_id):
    selected_book_indices, _ = get_user_true_response(self.db, user_id)
    if selected_book_indices:
        # 1-indexed 값을 0-indexed로 변환해서 cosine_similarity 접근
        selected_zero_indices = self.to_zero_index(selected_book_indices)
        # 선택한 책들이 속하는 클러스터를 판단해서 거기서 유사도가 높은 10개의 책을 추천한다.
        
        subset_embedding = self.embedding[selected_zero_indices] # 선택한 책의 임베딩 추출
        cluster_result = self.kmeans_model.predict(subset_embedding) # 클러스터 예측
        pick_books = np.array([], dtype=int)

        for cluster, sample_isbn in zip(cluster_result, selected_zero_indices):
          a = np.argsort(-self.cosine_similarity[sample_isbn]) + 1
          b = np.where(self.kmeans_model.labels_ == cluster)
          result = a[np.isin(a, b)][:10] # 
          pick_book = np.random.choice(result, 1) 
          pick_books = np.append(pick_books, pick_book)
        pick_books = np.random.choice(np.unique(pick_books), 5, replace=False) 
        result_recommended_books = self.isbn_arr[pick_books]
        
        # ####
        # average_similarity = self.cosine_similarity[selected_zero_indices, :].mean(axis=0)  # 열 방향 평균

        # ranked_indices = self.to_one_index(np.argsort(-average_similarity))  # 이 값은 0-index 기준
        # remove_selected_indices = ranked_indices[~np.isin(ranked_indices, selected_zero_indices)][:5]
        
        # # 추천 결과를 1-indexed로 변환하여 반환
        # recommended_books = list(map(int, remove_selected_indices))
        # result_recommended_books = self.isbn_arr[recommended_books]
        return [int(isbn) for isbn in result_recommended_books]  # ✅ numpy.int64 → int 변환
    else:
        # self.book_indices는 이미 1-indexed이므로 그대로 사용
        return list(map(int, np.random.choice(self.isbn_arr, 5)))