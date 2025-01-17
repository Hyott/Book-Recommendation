# 테이블 생성

def create_tables(conn):
    queries = [
        """
        CREATE TABLE IF NOT EXISTS books (
            isbn VARCHAR(30) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            publisher VARCHAR(255),
            publication_date DATE,
            description TEXT,
            key_sentences TEXT,
            image VARCHAR(2083),
            category VARCHAR(100)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS book_authors (
            author_id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            isbn VARCHAR(30) NOT NULL,
            FOREIGN KEY (isbn) REFERENCES books (isbn) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS tags (
            tag_id SERIAL PRIMARY KEY,
            tag_name VARCHAR(50) UNIQUE NOT NULL,
            category VARCHAR(100)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS book_tags (
            isbn VARCHAR(30),
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
                print("Query executed successfully!num:1")
            except Exception as e:
                conn.rollback()  # 특정 쿼리에서 실패하면 롤백
                print(f"Error executing query: {e}")
    except Exception as e:
        print("Error during table creation process:", e)
    finally:
        cursor.close()