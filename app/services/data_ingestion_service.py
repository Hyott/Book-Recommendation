# 테이블 생성

def create_tables(conn):
    queries = [
        """
        CREATE TABLE IF NOT EXISTS books (
            isbn VARCHAR(20) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            publisher VARCHAR(255),
            author VARCHAR(255),
            description TEXT
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS book_highlights (
            isbn VARCHAR(20),
            highlight TEXT NOT NULL,
            FOREIGN KEY (isbn) REFERENCES books (isbn) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS tags (
            tag_id SERIAL PRIMARY KEY,
            tag_name VARCHAR(50) UNIQUE NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS book_tags (
            isbn VARCHAR(20),
            tag_id INT,
            PRIMARY KEY (isbn, tag_id),
            FOREIGN KEY (isbn) REFERENCES books (isbn) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags (tag_id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS user_choice_tags (
            user_id INT,
            tag_id INT,
            PRIMARY KEY (user_id, tag_id),
            FOREIGN KEY (tag_id) REFERENCES tags (tag_id) ON DELETE CASCADE
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
                print("Query executed successfully!")
            except Exception as e:
                conn.rollback()  # 특정 쿼리에서 실패하면 롤백
                print(f"Error executing query: {e}")
    except Exception as e:
        print("Error during table creation process:", e)
    finally:
        cursor.close()


# 샘플 데이터 삽입(모두 테스트 뒤 삭제 예정)
def insert_sample_data(conn):
    """샘플 데이터 삽입"""
    sample_queries = [
        """
        INSERT INTO books (isbn, title, publisher, author, description)
        VALUES
        ('9781234567897', 'Example Book', 'Example Publisher', 'John Doe', 'An example book for testing.')
        ON CONFLICT (isbn) DO NOTHING;
        """,
        """
        INSERT INTO tags (tag_name)
        VALUES
        ('Interesting'), ('Classic'), ('Educational')
        ON CONFLICT (tag_name) DO NOTHING;
        """,
        """
        INSERT INTO book_tags (isbn, tag_id)
        VALUES
        ('9781234567897', 1), ('9781234567897', 2)
        ON CONFLICT DO NOTHING;
        """,
        """
        INSERT INTO user_choice_tags (user_id, tag_id)
        VALUES
        (1, 1), (1, 3)
        ON CONFLICT DO NOTHING;
        """
    ]

    try:
        cursor = conn.cursor()
        for query in sample_queries:
            cursor.execute(query)
        conn.commit()  # 각 삽입 후 커밋
        print("Sample data inserted successfully!")
    except Exception as e:
        conn.rollback()  # 삽입 중 오류 발생 시 롤백
        print("Error inserting sample data:", e)
    finally:
        cursor.close()