# books, books_authors table

import json

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
            # books 테이블 데이터 삽입
            book_query = """
            INSERT INTO books (isbn, title, publisher, publication_date, description, image, key_sentences, category)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (isbn) DO NOTHING;
            """
            cursor.execute(book_query, (
                entry.get('isbn13'),                      # isbn
                entry.get('title'),                       # title
                entry.get('publisher'),                   # publisher
                entry.get('publication_date'),                    # publication_date
                entry.get('description'),                 # description
                entry.get('img_url'),                       # image
                entry.get('key_sentences'),               # key_sentences
                "essay"                                   # category
            ))

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
        print('JSON 데이터를 데이터베이스에 성공적으로 삽입했습니다!')

    except Exception as e:
        conn.rollback()
        print(f"데이터 삽입 중 오류 발생: {e}")
    
    finally:
        cursor.close()