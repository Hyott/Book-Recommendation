from .connection import setup_database_and_tables
from sqlalchemy.orm import sessionmaker
import json
from sqlalchemy.exc import IntegrityError
from .models import BookTable, SentenceTable, TagTable
from .connection import database_engine, drop_all_tabal
from dotenv import load_dotenv
import os
import re

# .env 파일 로드
load_dotenv()

# 환경 변수 가져오기
host = os.getenv("HOST")
port = os.getenv("PORT")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
database_name = os.getenv("DATABASE_NAME")

engine = database_engine(host, port, user, password, database_name)
drop_all_tabal(engine)
setup_database_and_tables(host, port, user, password, database_name)


Session = sessionmaker(bind=engine)
session = Session()



json_file_path = 'data/scraping/all_book_data_ver_cleaned_JY.json'
print('books 테이블에 데이터를 넣습니다.')
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

json_file_path = 'data/scraping/llm_output_fixed.json'
print('sentences 테이블에 데이터를 넣습니다.')
with open(json_file_path, 'r', encoding='utf-8') as file:
  data = json.load(file)

  tag_id = 1
  for book_key in data:
    book = data[book_key]
    isbn = str(book["isbn"])
    sentence_text = book["sentence"]
    hashtags = book["hashtags"]

    book_sentence = SentenceTable(
                isbn=isbn,
                sentence=sentence_text,
            )
    try:
      session.merge(book_sentence)
      session.commit()
    except IntegrityError:
      session.rollback()
      print(f"중복된 ISBN: {isbn} - 'sentences' 삽입을 건너뜁니다.")
    except Exception as e:
        session.rollback()
        print(f"오류 발생: {e}")


    cleaned_tags = re.findall(r"#([^\s#\d.][^#]*)", hashtags)

    for tag in cleaned_tags:
      tag_entry = TagTable(
        id = tag_id,
        isbn = isbn,
        tag_name = tag.strip()
      )
      try:
        session.add(tag_entry)
        session.commit()
        tag_id += 1
      except IntegrityError:
        session.rollback()
        print(f"중복된 ISBN: {isbn} - {tag.strip()} 삽입을 건너뜁니다.")
      except Exception as e:
          session.rollback()
          print(f"오류 발생: {e}")


session.close()