# 테이블 생성
def create_tables(conn):
    queries = [
        """
        CREATE TABLE IF NOT EXISTS books (
            isbn VARCHAR(30) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            publisher VARCHAR(255),
            author VARCHAR(255),
            image_url VARCHAR(2083),
            category VARCHAR(100),
            description TEXT,  -- JSON 배열을 사용하여 설명 저장
            key_sentences TEXT  -- 핵심 문장도 JSON 배열로 저장
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS tags (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) UNIQUE NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS sentences (
            id SERIAL PRIMARY KEY,
            isbn VARCHAR(30) NOT NULL,
            sentence TEXT NOT NULL,
            FOREIGN KEY (isbn) REFERENCES books (isbn) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS book_tags (
            isbn VARCHAR(30),
            tag_id INT,
            PRIMARY KEY (isbn, tag_id),
            FOREIGN KEY (isbn) REFERENCES books (isbn) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS user_responses (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            question_number INT NOT NULL, -- 몇 번째 질문인지
            sentence_id INT NOT NULL,  -- 사용자가 선택한 핵심 문장 ID
            is_positive BOOLEAN, -- 응답 긍정 여부 추가
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sentence_id) REFERENCES sentences (id) ON DELETE CASCADE
        );
        """
    ]

    cursor = None
    try:
        cursor = conn.cursor()
        for query in queries:
            try:
                cursor.execute(query)
                conn.commit()  # 각 쿼리를 개별적으로 커밋
                print("✅ Query executed successfully!")
            except Exception as e:
                conn.rollback()  # 특정 쿼리에서 실패하면 롤백
                print(f"❌ Error executing query: {e}")
    except Exception as e:
        print(f"❌ Error during table creation process: {e}")
    finally:
        if cursor:
            cursor.close()
