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



def insert_hashtag_message_data(cursor, json_file):
    """
    llm.json 파일을 읽고, sentences, tags, book_tags 테이블에 데이터를 삽입한다.
    """
    with open(json_file, "r", encoding="utf-8") as f:
        books_data = json.load(f)

    tag_map = {}  # 태그 이름 -> tag_id 매핑

    for book_key, book_info in books_data.items():
        isbn = str(book_info["isbn13"])  # ISBN을 문자열로 변환
        sentence = book_info["message"]  # 핵심 문장
        hashtags = book_info["hashtags"].split("#")[1:]  # 태그 리스트 (첫 # 제거 후 리스트화)

        # 🔹 1. sentences 테이블에 데이터 삽입
        cursor.execute(
            "INSERT INTO sentences (isbn, sentence) VALUES (%s, %s) RETURNING id;",
            (isbn, sentence)
        )
        sentence_id = cursor.fetchone()[0]

        # 🔹 2. tags 테이블에 태그 삽입 (중복 방지)
        for tag in hashtags:
            tag = tag.strip()
            if tag not in tag_map:
                cursor.execute("SELECT id FROM tags WHERE name = %s;", (tag,))
                tag_id = cursor.fetchone()

                if tag_id is None:
                    cursor.execute(
                        "INSERT INTO tags (name) VALUES (%s) RETURNING id;",
                        (tag,)
                    )
                    tag_id = cursor.fetchone()[0]
                else:
                    tag_id = tag_id[0]

                tag_map[tag] = tag_id  # 태그 매핑 저장

            # 🔹 3. book_tags 테이블에 isbn과 tag_id 삽입 (중복 방지)
            cursor.execute(
                "INSERT INTO book_tags (isbn, tag_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (isbn, tag_map[tag])
            )
