from connection import setup_database_and_tables
from sqlalchemy.orm import sessionmaker
import json
from sqlalchemy.exc import IntegrityError
from models import BookTable
from connection import database_engine
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수 가져오기
host = os.getenv("HOST")
port = os.getenv("PORT")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
database_name = os.getenv("DATABASE_NAME")

setup_database_and_tables(host, port, user, password, database_name)
engine = database_engine(host, port, user, password, database_name)

Session = sessionmaker(bind=engine)
session = Session()

json_file_path = '../../data/scraping/all_book_data_ver_cleaned_JY.json'
with open(json_file_path, 'r', encoding='utf-8') as file:
  data = json.load(file)
  for book in data:      
    book_entry = BookTable(
                isbn=book["isbn13"],
                title=book["title"],
                publisher=book["publisher"],
                author=book["author"],
                image_url=book["img_url"],
                category='essay',
                publication_date = book["publication_date"]
            )
    try:
      session.merge(book_entry)
      session.commit()
    except IntegrityError:
      session.rollback()
      print(f"중복된 ISBN: {book.isbn} - 삽입을 건너뜁니다.")
    except Exception as e:
        session.rollback()
        print(f"오류 발생: {e}")

session.close()