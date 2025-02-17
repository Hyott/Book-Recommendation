FROM python:3.9
WORKDIR /app

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y netcat-traditional

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 실행 권한 부여
RUN chmod +x /app/start.sh

# start.sh 실행
CMD ["bash", "start.sh"]
