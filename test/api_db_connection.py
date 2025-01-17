#### FASTAPI에서 PostgreSQL 연결

from fastapi import FastAPI, Depends
from sqlalchemy import Column, String, Date, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List
import psycopg2

# PostgreSQL 데이터베이스 연결 정보
DATABASE_URL = "postgresql://sesac:1234@localhost:5432/book_recommend"

# SQLAlchemy 엔진 및 세션 설정
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# FastAPI 앱 생성
app = FastAPI()

# 모델 정의
class Book(Base):
    __tablename__ = "books"

    isbn = Column(String(30), primary_key=True)
    title = Column(String(255), nullable=False)
    publisher = Column(String(255))
    publication_date = Column(Date)
    description = Column(Text)
    key_sentences = Column(Text)
    image = Column(String(2083))
    category = Column(String(100))

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# 📌 Pydantic 모델 (FastAPI에서 요청/응답 처리)
class BookCreate(BaseModel):
    isbn: str
    title: str
    publisher: str
    publication_date: str
    description: str
    key_sentences: str
    image: str
    category: str

class BookResponse(BaseModel):
    isbn: str
    title: str
    publisher: str
    publication_date: str
    image: str


# 의존성 주입을 위한 DB 세션 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

    
# 모든 책 목록 조회 API
@app.get("/books/", response_model=List[BookResponse])
def get_books(db:Session = Depends(get_db)):
    books = db.query(Book).all()
    return books

# 특정 책 조회 API
@app.get("/books/{isbn}", response_model=BookResponse)
def get_book(isbn: str, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.isbn == isbn).first()
    if book:
        return book
    return {"error": "Book not found"}

# 책 추가 API (Pydantic 모델 사용)
@app.post("/books/")
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    new_book = Book(**book.dict())
    db.add(new_book)
    db.commit()
    return {"message": "Book added successfully"}