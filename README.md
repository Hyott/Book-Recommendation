# 📚 fromSentence (AI 기반 북 큐레이션 서비스)

## 📌 프로젝트 소개
fromSentence는 사용자의 독서 취향을 정밀하게 분석하여 맞춤형 에세이 도서를 추천하는 인공지능 기반 북 큐레이션 서비스 앱입니다. 
이 프로젝트는 질문을 통해 사용자가 선호하는 책의 취향을 파악하고, 선택에 따라 최적의 도서를 추천하는 시스템을 구축합니다. FastAPI를 활용하여 책 정보와 사용자 정보를 주고받으며, RAG와 LLM을 활용하여 보다 감성적이고 핵심적인 추천 문장을 생성합니다. 또한, 핵심 문장을 벡터화하여 유사한 책들 간의 비교 및 추천을 더욱 정교하게 수행합니다.

### Team

<table>
  <tr>
    <td align="center"><img src="https://github.com/heabppi.png" width="130" height="130" alt="박서현"></td>
    <td align="center"><img src="https://github.com/seo9045.png" width="130" height="150" alt="서예은"></td>
    <td align="center"><img src="https://github.com/Hyott.png" width="150" height="150" alt="안효철"></td>
  </tr>
  <tr>
    <td align="center"><b>박서현</b></td>
    <td align="center"><b>서예은</b></td>
    <td align="center"><b>안효철</b></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/heabppi">@heabppi</a></td>
    <td align="center"><a href="https://github.com/seo9045">@seo9045</a></td>
    <td align="center"><a href="https://github.com/Hyott">@Hyott</a></td>
  </tr>
</table>

<br>

### 🎖 Special Thanks
- **Mentor:** [JinYeong Choi](https://www.linkedin.com/in/jin0choi/)

<br>

## 역할 분담
#### 🧸 박서현 : Backend, PM

#### 👩‍💻 서예은 : Frontend, UI/UX

#### 👨‍💻 안효철 : Recommender System, Backend

#### 👨‍💻 최진영 : DevOps/Infrastructure

<br>
<br>

 ##  1.  주요 기능
⭐️ **사용자의 취향 발견**
- 사용자의 답변을 바탕으로 취향 맞춤형 에세이 도서를 추천
- 핵심 문장을 벡터화하여 여러 유사한 책들도 함께 추천


⭐️ **LLM을 사용한 생성 문장 활용**
- 책의 핵심 문장과 설명을 포괄하여 LLM에 입력
- 보다 정확하고 감성적인 생성 문장을 생성하여 사용자의 선택 과정에서 몰입감 제공


⭐️ **취향 공유 및 소셜 기능**
- 사용자의 취향을 반영한 추천 결과를 공유
- 책 추천을 통해 독서 문화 활성화


⭐️ **개인화된 추천 알고리즘**
- 다중 클러스터링을 활용한 탐색-활용 균형 조정
- 사용자 선택 데이터를 기반으로 점진적 학습을 진행하여 더욱 정교한 추천 제공

⭐️ **데이터 기반 추천 시스템**
- 책 임베딩을 활용하여 코사인 유사도를 기반으로 유사 도서를 추천
- RAG(Retrieval-Augmented Generation) 기법을 활용하여 보다 정밀한 추천 구현

<br>

## 2. 개발 환경
| 카테고리 | 기술 스택 |
|:----------:|:----------:|
| **Backend** | FastAPI, PostgreSQL |
| **Frontend** | Flutter |
| **UI/UX** | figma |
| **Recommender System** | RAG |
| **DevOps/Infrastructure** | Docker|
| **Communication** | Git, Slack, Notion|


## 3. 프로젝트 구조
```
📦 book_recommedation
 ┣ 📂 app
 ┃ ┣ 📂 database  
 ┃     ┣ __init__.py
 ┃ ┣ 📂 services  
 ┃ ┣ 📜 __init__.py
 ┃ ┣ 📜 Dockerfile.py
 ┃ ┣ 📜 main.py
 ┣ 📂 data
 ┣ 📂 flutter_app
 ┣ 📂 notebook
 ┣ 📂 test
 ┣  docker-compose.yml
 ┣  config.py    
?┣  requirements.txt  
 ┗  README.md
```

<br>

## 4. 개발 기간 및 작업 관리
#### 🗓 개발 기간
- 전체 개발 기간 : 2025-01-06 ~ 2025-02-17
- 데이터베이스 구현 및 알고리즘 설계 : 2025-01-06 ~ 2025-02-03
- API 연동 및 앱 개발 : 2025-02-04 ~ 2025-02-17

#### 🛠 작업 관리
- GitHub & Slack : 진행 상황 공유 및 코드 관리
- Notion : 회의록 정리 및 작업 일정 관리

<br>

## 5. 목표
- 사용자가 쉽게 참여할 수 있고 몰입감 있는 취향 분석 설계
- 개인화된 맞춤 도서 추천 알고리즘 개발
- 벡터화된 핵심 문장 기반의 정밀한 추천 시스템 구현

<br>

## 6. 페이지별 기능
- **메인 페이지 :** 도서 추천 테스트 진입
- **핵심문장 선택 페이지 :** 질문에 답변하여 취향 분석
- **추천 결과 페이지 :** 사용자 취향에 맞는 여러 권의 책 추천
- **책 상세 및 공유 페이지 :** 추천된 책의 정보 및 리뷰 제공, 공유 가능 기능

<br>

## 📢 프로젝트 후기
#### 👩‍💻 서예은 :

#### 👨‍💻 안효철 : 문제정의 부터 배포까지 전 과정을 경험할 수 있는 값진 프로젝트였습니다.

#### 🧸 박서현 :

#### 👨‍💻 mentor.최진영 :
