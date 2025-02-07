import os
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from app.database.models import BookTable, TagTable, SentenceTable, BookTagTable, UserResponseTable
from app.database.connection import database_engine
from app.services.book_rec_logic import question_number
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

# 데이터베이스 연결 설정
host = os.getenv("HOST")
port = os.getenv("PORT")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
database_name = os.getenv("DATABASE_NAME")

engine = database_engine(host, port, user, password, database_name)


def get_choice_bool(user_id: int, question_num: int, db: Session):
    """
    특정 사용자의 질문 응답 데이터를 조회하는 함수
    """
    try :
        user_responses = (
            db.query(UserResponseTable).filter(UserResponseTable.user_id == user_id, UserResponseTable.question_number == question_num).all()
        )

        if len(user_responses) < 2:
            return None, None
    
        book_a_select = user_responses[0].is_positive
        book_b_select = user_responses[1].is_positive
    
        return book_a_select, book_b_select
    except Exception as e:
        print(f"데이터 조회 중 오류 발생: {e}")
        return None, None


# 기존 코드
# 데이터베이스 연결 설정
host = "localhost"
port = 5432
user = "postgres"
password = "1234"
database_name = "book_recommend"

engine = database_engine(host, port, user, password, database_name)


conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname="book_recommend"
        )
conn.autocommit = True
cursor = conn.cursor()


def get_choice_bool():
    cursor.execute(
        sql.SQL("SELECT * FROM public.user_responses WHERE user_id = %s and question_number = %s"),
        (101, question_number)
    )
    exists = cursor.fetchall()
    book_a_select = exists[0][4]
    book_b_select = exists[1][4]

    return book_a_select, book_b_select


# exists = cursor.fetchone()