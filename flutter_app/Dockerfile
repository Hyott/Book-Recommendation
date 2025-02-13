# Flutter 빌드 환경 설정
FROM debian:latest AS build-env

# 필수 패키지 설치
RUN apt-get update
RUN apt-get install -y curl git unzip

# Flutter SDK 및 프로젝트 변수 정의
ARG FLUTTER_SDK=/usr/local/flutter
ARG FLUTTER_VERSION=3.27.1
ARG APP=/app

# Flutter 설치 및 버전 체크아웃
RUN git clone https://github.com/flutter/flutter.git $FLUTTER_SDK
RUN cd $FLUTTER_SDK && git fetch && git checkout $FLUTTER_VERSION

# 환경 변수 설정
ENV PATH="$FLUTTER_SDK/bin:$FLUTTER_SDK/bin/cache/dart-sdk/bin:${PATH}"

# Flutter 설치 확인
RUN flutter doctor -v

# 애플리케이션 디렉토리 생성
RUN mkdir $APP
COPY . $APP
WORKDIR $APP

# Flutter 빌드 수행
RUN flutter clean
RUN flutter pub get
RUN flutter build web

# Nginx로 배포 설정
FROM nginx:1.25.2-alpine

# 빌드된 웹 파일을 올바른 경로에서 복사
COPY --from=build-env /app/build/web /usr/share/nginx/html

# Nginx 실행
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]