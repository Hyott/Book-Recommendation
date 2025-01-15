# 데이터베이스 연결과 관련 된 코드
import psycopg2
from pydantic import BaseModel

class DatabaseSettings(BaseModel):
    host: str = 'localhost'
    port: int = 5432
    database: str = 'book_recommend'
    user: str = 'sesac'
    password: str = '1234'

    print('Database settings successfully!')


# 데이터베이스 연결 함수
def create_connection(settings: DatabaseSettings):
    """데이터베이스 연결 생성"""
    try:
        conn = psycopg2.connect(
            host=settings.host,
            port=settings.port,
            database=settings.database,
            user=settings.user,
            password=settings.password
        )
        print("Database connected successfully!")
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None