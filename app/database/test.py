import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from app.database.models import BookTable, TagTable, SentenceTable, BookTagTable, UserResponseTable
from app.database.connection import database_engine
from app.services.book_rec_logic import question_number
import psycopg2
from psycopg2 import sql

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