# 책 데이터를 가져오는 로직
# DB에서 테이블 데이터를 가져와 API 응답으로 변환
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.database.models import Book, NewBooks

def get_books(db: Session, skip: int = 0, limit: int = 10):
    books = db.query(Book).offset(skip).limit(limit).all()
    if not books:
        raise HTTPException(status_code=404, detail="No books found")

    return [
        {
            "isbn": book.isbn,
            "title": book.title,
            "author": book.author,
            "publisher": book.publisher,
            "category": book.category,
            "image_url": book.image_url,
            "description": " ".join(book.description) if book.description else None,
            "key_sentences": " ".join(book.key_sentences) if book.key_sentences else None,
        }
        for book in books
    ]

def get_new_books(db: Session, skip: int = 0, limit: int = 10):
    books = db.query(NewBooks).offset(skip).limit(limit).all()
    if not books:
        raise HTTPException(status_code=404, detail="No books found")

    return [
        {
            "isbn": book.isbn,
            "message": book.message,
            "hashtags": book.hashtags.split() if book.hashtags else []
        }
        for book in books
    ]
