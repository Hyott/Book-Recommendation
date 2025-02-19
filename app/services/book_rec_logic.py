import numpy as np

class RecommendationEngine:
    def __init__(self):
      self.cosine_similarity = np.load("../app/data/cosine_similarity.npy")  # 인스턴스 변수
      self.embedding = np.load("../app/data/embedding.npy")  # 인스턴스 변수
      self.book_indices = np.arange(len(self.embedding))
    
    def get_user_response(self):
      return 
    
    
    # 유저 아이디가 
    def filter_top_70_percent(self):
      """
      현재 벡터들에서 코사인 유사도를 기반으로 상위 70% 벡터만 남기는 함수
      """
      # ✅ 랜덤으로 벡터 하나 선택 (현재 남아있는 벡터 중)
      random_idx = np.random.choice(len(self.embedding), 1)[0]

      # ✅ 선택된 벡터와 유사한 순서대로 정렬
      sorted_indices = np.argsort(-self.cosine_similarity[random_idx])

      # ✅ 상위 70% 벡터만 선택
      num_keep = int(len(sorted_indices) * 0.57)
      top_indices = sorted_indices[:num_keep]
      
      self.embedding = self.embedding[top_indices]
      self.book_indices = self.book_indices[top_indices]
      