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
    if result:
        return int(result[0])
    else:
        return 0

def get_user_last_sentenceid(db: Session, user_id: str):
    result = db.query(UserResponseTable.sentence_id) \
            .filter(UserResponseTable.user_id == user_id) \
            .filter(UserResponseTable.is_positive == True) \
            .order_by(UserResponseTable.question_number.desc()) \
            .first()
         # .first()[0]) # 가장 최신 값 가져오기 
    if result:
        return int(result[0])
    else:
        return 0
    
def get_sentences_by_ids(db: Session, sentence_ids: list[int]):
    return db.query(SentenceTable).filter(SentenceTable.id.in_(sentence_ids)).all()

def get_user_true_response(db: Session, user_id: str):
    result = db.query(UserResponseTable.question_number,
                      UserResponseTable.sentence_id) \
               .filter(UserResponseTable.user_id == user_id) \
               .filter(UserResponseTable.is_positive == True) \
               .all()
    
    sentence_ids = [row.sentence_id for row in result] if result else []
    max_question_number = max((row.question_number for row in result) , default=0) + 1
    
    return sentence_ids, max_question_number

def get_presented_sentence(db: Session, user_id: str):
    result = db.query(UserResponseTable.sentence_id) \
               .filter(UserResponseTable.user_id == user_id) \
               .all()
    
    sentence_ids = [row.sentence_id for row in result] if result else []
    
    return sentence_ids