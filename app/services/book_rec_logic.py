import numpy as np
from database.crud import get_user_response

class RecommendationEngine:
  def __init__(self, db):
    self.cosine_similarity = np.load("data/cosine_similarity.npy")  # 인스턴스 변수
    self.embedding = np.load("data/embedding.npy")  # 인스턴스 변수
    self.isbn_arr = np.load("data/isbn_arr.npy")
    self.book_indices = np.arange(1, len(self.cosine_similarity) + 1)
    self.db = db
    
  def to_zero_index(self, indices):
    # 1-indexed 리스트나 배열을 0-indexed로 변환
    return np.array(indices) - 1

  def to_one_index(self, indices):
      # 0-indexed 리스트나 배열을 1-indexed로 변환
      return np.array(indices) + 1
    
  def get_book_options(self, user_id):
    selected_book_indices, question_number = get_user_response(self.db, user_id)
    if selected_book_indices:
        # 1-indexed 값을 0-indexed로 변환해서 cosine_similarity 접근
        selected_zero_indices = self.to_zero_index(selected_book_indices)
        average_similarity = self.cosine_similarity[selected_zero_indices, :].mean(axis=0)  # 열 방향 평균

        ranked_indices = np.argsort(-average_similarity)  # 이 값은 0-index 기준
        # 0-index 기준으로 선택된 인덱스를 제외한 후, 상위 1000개 선택
        remove_selected_indices = ranked_indices[~np.isin(ranked_indices, selected_zero_indices)][:1000]
        # 추천 결과를 1-indexed로 변환하여 반환
        recommended_books = list(map(int, self.to_one_index(np.random.choice(remove_selected_indices, 2))))
        return recommended_books, question_number
    else:
        # self.book_indices는 이미 1-indexed이므로 그대로 사용
        return list(map(int, np.random.choice(self.book_indices, 2))), question_number

  
  def get_result_isbn(self, user_id):
    selected_book_indices, _ = get_user_response(self.db, user_id)
    if selected_book_indices:
        # 1-indexed 값을 0-indexed로 변환해서 cosine_similarity 접근
        selected_zero_indices = self.to_zero_index(selected_book_indices)
        average_similarity = self.cosine_similarity[selected_zero_indices, :].mean(axis=0)  # 열 방향 평균

        ranked_indices = np.argsort(-average_similarity)  # 이 값은 0-index 기준
        # 0-index 기준으로 선택된 인덱스를 제외한 후, 상위 1000개 선택
        remove_selected_indices = ranked_indices[~np.isin(ranked_indices, selected_zero_indices)][:5]
        
        # 추천 결과를 1-indexed로 변환하여 반환
        recommended_books = list(map(int, self.to_one_index(remove_selected_indices)))
        result_recommended_books = self.isbn_arr[recommended_books]
        return [int(isbn) for isbn in result_recommended_books]  # ✅ numpy.int64 → int 변환
    else:
        # self.book_indices는 이미 1-indexed이므로 그대로 사용
        return list(map(int, np.random.choice(self.isbn_arr, 5)))