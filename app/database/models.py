from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, func
from zoneinfo import ZoneInfo
from datetime import datetime
from pydantic import BaseModel

Base = declarative_base()

class BookTable(Base):
    __tablename__ = "books"
    isbn = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    publisher = Column(String, nullable=False)
    author = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    category = Column(String, nullable=False)
    publication_date = Column(DateTime, nullable=False)

class TagTable(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    isbn = Column(String, ForeignKey("books.isbn"), primary_key=True)
    tag_name = Column(String, nullable=False)
    date = Column(DateTime, default=func.now(), onupdate=func.now())

class SentenceTable(Base):
    __tablename__ = "sentences"
    id = Column(Integer, primary_key=True, autoincrement=True)
    isbn = Column(String, ForeignKey("books.isbn"), nullable=False)
    sentence = Column(String, nullable=False)

class UserResponseTable(Base):
    __tablename__ = "user_responses"
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)  
    question_number = Column(Integer, nullable=False)
    sentence_id = Column(Integer, ForeignKey("sentences.id"), nullable=False)
    is_positive = Column(Boolean, nullable=False)
    datetime = Column(DateTime, default=datetime.now(ZoneInfo("Asia/Seoul")), nullable=True)