from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from database.crud import get_book_by_isbn, get_sentence_by_isbn, add_user_response
from database.schemas import BookSchema, SentenceSchema, UserResponseSchema
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용 (배포 시 특정 도메인으로 제한 추천)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# ✅ 특정 ISBN으로 도서 조회 API
@app.get("/books/{isbn}", response_model=BookSchema)
def read_book(isbn: str, db: Session = Depends(get_db)):
    book = get_book_by_isbn(db, isbn)
    if book is None:
        raise HTTPException(status_code=404, detail="해당 ISBN의 도서를 찾을 수 없습니다.")
    return book

# ✅ 특정 ISBN으로 생성문장 조회 API
@app.get("/sentences/{isbn}", response_model=SentenceSchema)
def read_book(isbn: str, db: Session = Depends(get_db)):
    sentence = get_sentence_by_isbn(db, isbn)
    if sentence is None:
        raise HTTPException(status_code=404, detail="해당 ISBN의 생성문장을 찾을 수 없습니다.")
    return sentence


@app.post("/user_responses/")
def create_user_response(response: UserResponseSchema, db: Session = Depends(get_db)):
    stmt = add_user_response(response)
    db.execute(stmt)
    db.commit()
    return response