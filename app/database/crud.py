from sqlalchemy.orm import Session
from .models import BookTable, SentenceTable, UserResponseTable, TagTable
from .schemas import UserResponseSchema
from datetime import datetime
from zoneinfo import ZoneInfo
import uuid
from sqlalchemy.dialects.postgresql import insert


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
    stmt = insert(UserResponseTable).values(
            user_id=user_id,
            question_number=response.question_number,
            # sentence_id=response.sentence_id,
            sentence_id=response.sentence_id,
            is_positive=response.is_positive,
            datetime=datetime.now(ZoneInfo("Asia/Seoul"))
        ).on_conflict_do_nothing()
    return stmt

def get_question_number_by_user_id(db: Session, user_id: str):
    result = db.query(UserResponseTable.question_number) \
            .filter(UserResponseTable.user_id == user_id) \
            .order_by(UserResponseTable.question_number.desc()) \
            .first()
         # .first()[0]) # 가장 최신 값 가져오기

    if result is None:
        return 0  # 데이터가 없으면 기본값 0 반환
    
    return int(result.question_number)  # 첫 번째 컬럼 값 반환