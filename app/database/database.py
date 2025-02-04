from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수 가져오기
host = os.getenv("HOST")
port = os.getenv("PORT")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
database_name = os.getenv("DATABASE_NAME")

# ✅ 엔진 생성
engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database_name}")

# ✅ 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ 데이터베이스 세션 의존성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
