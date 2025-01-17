# books, books_authors table

import json
import datetime

def insert_books_and_authors(conn, json_file):
    """ 
    Json 파일 데이터를 books 및 book_authors 테이블에 삽입
    """
    try:
        # JSON 파일 읽기
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 데이터베이스 커서 생성
        cursor = conn.cursor()

        for entry in data:

            # 📌 날짜 변환 (문자열 -> DATE)
            pub_date_str = entry.get('publication_date', None)
            pub_date = None  # 기본값

            if pub_date_str:
                try:
                    pub_date = datetime.datetime.strptime(pub_date_str, "%Y-%m-%d").date()
                except ValueError:
                    print(f"⚠️ 날짜 형식 오류: {pub_date_str} (책: {entry.get('title', 'Unknown Title')})")
                    continue  # 날짜 형식 오류가 있으면 해당 데이터 스킵

            # 📌 이미지 URL 변환 (예: \/ → /)
            img_url = entry.get("img_url", "").replace("\\/", "/")

            # books 테이블 데이터 삽입
            book_query = """
            INSERT INTO books (isbn, title, publisher, publication_date, description, key_sentences, image, category)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (isbn) DO NOTHING;
            """
            try:
                cursor.execute(book_query, (
                    entry.get('isbn13'),
                    entry.get('title'),
                    entry.get('publisher'),
                    pub_date,  # 변환된 날짜 값
                    entry.get('description'),
                    entry.get('key_sentences'),
                    img_url,  # 변환된 이미지 URL
                    "essay",  # 모든 항목에 대해 'essay'로 설정
            ))
            
            except Exception as e:
                print(f"❌ 데이터 삽입 중 오류 발생: {e}")
                print(f"   📌 오류 데이터 -> ISBN: {entry.get('isbn13')}, 제목: {entry.get('title', 'Unknown Title')}")
                continue  # 해당 데이터 스킵

            # 작가 이름이 쉼표로 구분된 경우 처리
            authors = entry.get('author', "")
            author_list = [author.strip() for author in authors.split(",")] if authors else []

            # book_authors 테이블에 각 작가 이름 삽입
            for author in author_list:
                author_query = """
                INSERT INTO book_authors (name, isbn)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
                """
                cursor.execute(author_query, (
                    author,
                    entry.get('isbn13')
                ))
            
        # 변경사항 커밋
        conn.commit()
        print('JSON 데이터를 데이터베이스에 성공적으로 삽입했습니다!num:1')

    except Exception as e:
        conn.rollback()
        print(f"데이터 삽입 중 오류 발생: {e}")
    
    finally:
        cursor.close()