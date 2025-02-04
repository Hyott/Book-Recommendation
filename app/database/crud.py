from sqlalchemy.orm import Session
from .models import BookTable, SentenceTable, UserResponseTable, TagTable
from .schemas import UserResponseSchema
from datetime import datetime
from zoneinfo import ZoneInfo
import uuid

# # ✅ 전체 도서 목록 조회
# def get_all_books(db: Session):
#     return db.query(BookTable).all()

# ✅ 특정 ISBN으로 도서 조회
def get_book_by_isbn(db: Session, isbn: str):
    return db.query(BookTable).filter(BookTable.isbn == isbn).first()

# ✅ 특정 ISBN으로 생성문장 조회 API
def get_sentence_by_isbn(db: Session, isbn: str):
    return db.query(SentenceTable).filter(SentenceTable.isbn == isbn).first()

# 특정 ISBN으로 tags 조회 API
def get_tags_by_isbn(db: Session, isbn: str):
    return db.query(TagTable.tag_name).filter(TagTable.isbn == isbn).all()


# ✅ 유저의 log 생성
def add_user_response(response: UserResponseSchema):
    user_id = response.user_id if response.user_id else str(uuid.uuid4())
    new_response = UserResponseTable(
            user_id=user_id,
            question_number=response.question_number,
            sentence_id=response.sentence_id,
            is_positive=response.is_positive,
            datetime=datetime.now(ZoneInfo("Asia/Seoul"))
        )
    return new_response