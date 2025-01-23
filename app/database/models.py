# 데이터베이스 테이블을 정의하는 SQLAlchemy 모델 클래스 모음
# 각 모델 정의
from sqlalchemy import Column, String, Text, ARRAY, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from .database import Base

class UserResponse(Base):
    __tablename__ = "user_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    question_number = Column(Integer, nullable=False)
    g_sentence_id = Column(Integer, ForeignKey("sentences.g_sentence_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())

class Book(Base):
    __tablename__ = "books"

    isbn = Column(String(30), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    publisher = Column(String(255))
    author = Column(String(255))
    image_url = Column(String(2083))
    category = Column(String(100))
    description = Column(ARRAY(Text))
    key_sentences = Column(ARRAY(Text))

class NewBooks(Base):
    __tablename__ = "new_books"

    isbn = Column(String(30), primary_key=True)
    message = Column(Text)
    hashtags = Column(String)
