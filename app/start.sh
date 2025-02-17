#!/bin/bash
echo "Waiting for database to be ready..."

# 데이터베이스가 준비될 때까지 대기
while ! nc -z $HOST $POSTGRES_PORT; do
  sleep 1
done

echo "Database is ready!"

# Alembic 마이그레이션 실행
alembic upgrade head

# FastAPI 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
