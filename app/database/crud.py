from sqlalchemy.orm import Session
from .models import BookTable

# ✅ 전체 도서 목록 조회
def get_all_books(db: Session):
    return db.query(BookTable).all()

# ✅ 특정 ISBN으로 도서 조회
def get_book_by_isbn(db: Session, isbn: str):
    return db.query(BookTable).filter(BookTable.isbn == isbn).first()
