import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine
from models import Base 

def ensure_database_exists(host, port, user, password, database_name):
    """
    데이터베이스가 존재하는지 확인하고, 없으면 생성하는 함수.

    Args:
        host (str): PostgreSQL 서버 호스트.
        port (int): PostgreSQL 서버 포트.
        user (str): 사용자 이름.
        password (str): 비밀번호.
        database_name (str): 확인하거나 생성할 데이터베이스 이름.

    Returns:
        str: 데이터베이스 상태 메시지.
    """
    try:
        # 기본 데이터베이스에 연결 (postgres)
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # 데이터베이스 존재 여부 확인
        cursor.execute(
            sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"),
            [database_name]
        )
        exists = cursor.fetchone()

        if exists:
            return f"Database '{database_name}' already exists."
        else:
            # 데이터베이스 생성
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(database_name)
                )
            )
            return f"Database '{database_name}' has been created."

    except psycopg2.Error as e:
        return f"Error: {e}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def setup_database_and_tables(host, port, user, password, database_name):
    """
    데이터베이스와 테이블을 설정하는 함수.
    """
    ensure_database_exists(host, port, user, password, database_name)

    # SQLAlchemy 엔진 생성
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database_name}")
    Base.metadata.create_all(engine)
    print(f"Tables created in database '{database_name}'.")

    return engine


def database_engine(host, port, user, password, database_name):
    return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database_name}")