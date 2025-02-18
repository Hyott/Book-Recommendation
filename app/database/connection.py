import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine, MetaData
from .models import Base 
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수 가져오기
host = os.getenv("HOST")
port = os.getenv("POSTGRES_PORT")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
database_name = os.getenv("DATABASE_NAME")




# ✅ UTF-8 설정된 엔진 생성
engine = create_engine(
    f"postgresql://{user}:{password}@{host}:{port}/{database_name}",
    connect_args={"options": "-c client_encoding=UTF8"}  # UTF-8 강제 설정
)

# ✅ 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
            dbname=database_name
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

def drop_all_tabal(engine):
    print("CASCADE 포함 모든 테이블을 삭제합니다...")

    # 데이터베이스 메타데이터 반영 (현재 DB에 존재하는 모든 테이블 감지)
    meta = MetaData()
    meta.reflect(bind=engine)

    # 모든 테이블 삭제 (CASCADE 포함)
    meta.drop_all(bind=engine)

    print("모든 테이블이 삭제되었습니다.")


def database_engine(host, port, user, password, database_name):
    return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database_name}")

# ✅ 데이터베이스 세션 의존성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()