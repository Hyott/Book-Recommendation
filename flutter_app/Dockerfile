# Flutter 웹앱 빌드
FROM cirrusci/flutter:latest AS build
WORKDIR /app
COPY . .
RUN flutter pub get
RUN flutter build web

# Nginx를 이용한 Flutter 웹앱 배포
FROM nginx:alpine
COPY --from=build /app/build/web /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
