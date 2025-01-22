from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, String, Text, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware


# Database 설정
DATABASE_URL = "postgresql://sesac:1234@localhost:5432/book_recommend"
# DATABASE_URL = "postgresql://sesac_yeeun:0823@211.34.202.232:5432/book_recommend"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 책 모델 정의 (테이블 스키마 반영)
class Book(Base):
    __tablename__ = "books"

    isbn = Column(String(30), primary_key=True, index=True)  # ISBN을 기본 키로 설정
    title = Column(String(255), nullable=False)
    publisher = Column(String(255))
    author = Column(String(255))
    image_url = Column(String(2083))  # URL 최대 길이 2083자
    category = Column(String(100))
    description = Column(ARRAY(Text))  # PostgreSQL ARRAY(TEXT) 타입
    key_sentences = Column(ARRAY(Text))  # PostgreSQL ARRAY(TEXT) 타입

# 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI 앱 생성
app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"],  # 모든 출처 허용 (배포 시 특정 도메인으로 제한 추천)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)
# DB 세션 가져오기
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 루트 엔드포인트 추가
@app.get("/")
def read_root():
    return {"message": "Welcome to the Book Recommendation API!"}

# 책 목록 가져오기 API
@app.get("/books/")
def get_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    books = db.query(Book).offset(skip).limit(limit).all()
    if not books:
        raise HTTPException(status_code=404, detail="No books found")
    
    books_list = []
    for book in books:
        books_list.append({
            "isbn": book.isbn,
            "title": book.title,
            "author": book.author,
            "publisher": book.publisher,
            "category": book.category,
            "image_url": book.image_url,
            "description": " ".join(book.description) if book.description else None,  # 문장으로 변환
            "key_sentences": " ".join(book.key_sentences) if book.key_sentences else None  # 문장으로 변환
        })
    return books_list
