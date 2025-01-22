import json
import psycopg2

def insert_books(conn, json_file):
    """📌 JSON 파일 데이터를 books 테이블에 삽입 (TEXT 컬럼에 그대로 저장)"""
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        cursor = conn.cursor()

        for entry in data:
            try:
                # 이미지 URL 변환
                img_url = entry.get("img_url", "").replace("\\/", "/")

                # 📌 books 테이블 데이터 삽입
                book_query = """
                INSERT INTO books (isbn, title, publisher, author, image_url, category, description, key_sentences)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (isbn) DO NOTHING;
                """
                cursor.execute(book_query, (
                    entry.get('isbn13'),
                    entry.get('title'),
                    entry.get('publisher'),
                    entry.get('author'),
                    img_url,
                    "essay",
                    entry.get("description", ""),   # ✅ 변환 없이 그대로 삽입
                    entry.get("key_sentences", "")  # ✅ 변환 없이 그대로 삽입
                ))

            except Exception as e:
                print(f"❌ 데이터 삽입 중 오류 발생: {e}")
                print(f"   📌 오류 데이터 -> ISBN: {entry.get('isbn13')}, 제목: {entry.get('title', 'Unknown Title')}")
                conn.rollback()  # 🔴 트랜잭션 롤백하여 다음 데이터 삽입 가능하도록 처리
                continue  # 다음 데이터로 이동

        conn.commit()  # 모든 데이터 정상 삽입 후 커밋
        print('✅ JSON 데이터를 데이터베이스에 성공적으로 삽입했습니다!')

    except Exception as e:
        conn.rollback()
        print(f"❌ 전체 데이터 삽입 중 오류 발생: {e}")

    finally:
        cursor.close()