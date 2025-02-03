from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database.connection import get_db
from .database.crud import get_all_books, get_book_by_isbn
from .database.schemas import BookSchema
from typing import List

app = FastAPI()

# ✅ 전체 도서 목록 조회 API
@app.get("/books", response_model=List[BookSchema])
def read_books(db: Session = Depends(get_db)):
    books = get_all_books(db)
    if not books:
        raise HTTPException(status_code=404, detail="도서 목록이 없습니다.")
    return books

# ✅ 특정 ISBN으로 도서 조회 API
@app.get("/books/{isbn}", response_model=BookSchema)
def read_book(isbn: str, db: Session = Depends(get_db)):
    book = get_book_by_isbn(db, isbn)
    if book is None:
        raise HTTPException(status_code=404, detail="해당 ISBN의 도서를 찾을 수 없습니다.")
    return book
