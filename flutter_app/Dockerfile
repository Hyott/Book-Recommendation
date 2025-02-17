# Flutter 빌드 환경 설정
FROM debian:latest AS build-env

# 필수 패키지 설치
RUN apt-get update
RUN apt-get install -y curl git unzip

# Flutter SDK 및 프로젝트 변수 정의
ARG FLUTTER_SDK=/usr/local/flutter
ARG FLUTTER_VERSION=3.27.1
ARG APP=/app
ARG API_BASE_URL

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

# Flutter 빌드 수행 (환경 변수 적용)
RUN flutter clean
RUN flutter pub get
RUN flutter build web --release --dart-define=API_BASE_URL=$API_BASE_URL
