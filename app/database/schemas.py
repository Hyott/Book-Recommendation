from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from zoneinfo import ZoneInfo

# 도서(Book) 스키마
class BookSchema(BaseModel):
    isbn: str
    title: str
    publisher: str
    author: str
    image_url: str
    category: str
    publication_date: datetime

    class Config:
        orm_mode = True  # ✅ SQLAlchemy ORM 모델과 호환되도록 설정


# 태그(Tag) 스키마
class TagSchema(BaseModel):
    id: int
    name: str
    isbn: str

    class Config:
        orm_mode = True


# 문장(Sentence) 스키마
class SentenceSchema(BaseModel):
    id: int
    isbn: str
    sentence: str

    class Config:
        orm_mode = True

# 사용자 응답(UserResponse) 스키마
class UserResponseSchema(BaseModel):
    user_id: str = Field(..., description="User ID 또는 UUID")
    question_number: int
    sentence_id: int
    is_positive: bool
    datetime: Optional[datetime] = Field(datetime.now(ZoneInfo("Asia/Seoul"))) # ✅ null 가능

    class Config:
        orm_mode = True