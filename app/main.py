# FASTAPI 앱을 실행하는 메인 파일
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database.database import engine, get_db
from app.database.models import Base
from app.services.book_service import get_books, get_new_books
from app.services.user_response_service import create_user_response, UserResponseCreate

# ✅ 테이블 생성 (최초 실행 시)
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Book Recommendation API!"}

@app.get("/books/")
def fetch_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_books(db, skip, limit)

@app.get("/newbooks/")
def fetch_new_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_new_books(db, skip, limit)

@app.post("/user_responses/")
def store_user_response(response: UserResponseCreate, db: Session = Depends(get_db)):
    return create_user_response(response, db)
