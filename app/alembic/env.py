import os
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv
from database.database import Base  # 기존 모델 import

# .env 파일 로드
load_dotenv()

# 환경 변수에서 데이터베이스 URL 생성
DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('DATABASE_NAME')}"

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# 모델의 메타데이터 등록
target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
