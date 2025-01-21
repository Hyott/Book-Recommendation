# books, books_authors table

import json
import datetime

def insert_books_and_authors(conn, json_file):
    """ 
    Json 파일 데이터를 books 테이블에 삽입
    """
    try:
        # JSON 파일 읽기
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 데이터베이스 커서 생성
        cursor = conn.cursor()

        for entry in data:

            # 📌 이미지 URL 변환 (예: \/ → /)
            img_url = entry.get("img_url", "").replace("\\/", "/")

            # books 테이블 데이터 삽입
            book_query = """
            INSERT INTO books (isbn, title, publisher, author, image_url, category)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (isbn) DO NOTHING;
            """
            try:
                cursor.execute(book_query, (
                    entry.get('isbn13'),
                    entry.get('title'),
                    entry.get('publisher'),
                    entry.get('author'),
                    img_url,  # 변환된 이미지 URL
                    "essay",  # 모든 항목에 대해 'essay'로 설정
            ))
            
            except Exception as e:
                print(f"❌ 데이터 삽입 중 오류 발생: {e}")
                print(f"   📌 오류 데이터 -> ISBN: {entry.get('isbn13')}, 제목: {entry.get('title', 'Unknown Title')}")
                continue  # 해당 데이터 스킵
            
            
        # 변경사항 커밋
        conn.commit()
        print('JSON 데이터를 데이터베이스에 성공적으로 삽입했습니다!num:1')

    except Exception as e:
        conn.rollback()
        print(f"데이터 삽입 중 오류 발생: {e}")
    
    finally:
        cursor.close()