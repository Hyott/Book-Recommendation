# 📚 fromSentence (AI 기반 책 큐레이션 서비스)

## 📌 프로젝트 소개
fromSentence는 사용자의 독서 취향을 정밀하게 분석하여 맞춤형 에세이 도서를 추천하는 인공지능 기반 북 큐레이션 서비스입니다. 
이 프로젝트는 질문을 통해 사용자의 선호도를 파악하고, 선택한 도서를 기반으로 최적의 추천을 제공하는 시스템을 구축합니다. FastAPI를 활용해 책 정보 및 사용자 데이터를 효율적으로 주고받으며, RAG와 LLM을 활용하여 각 도서의 작가 문체와 분위기를 반영한 감성적이고 핵심적인 추천 문장, 태그, 편지를 생성합니다. 또한, 추천 문장을 벡터화하고, Thompson Sampling 및 KMeans 클러스터링을 적용하여 유사한 책 간의 비교 및 추천을 더욱 정교하게 수행합니다. 이를 통해 감성과 효율을 동시에 담아, 사용자가 보다 깊이 있는 독서 경험을 할 수 있도록 돕는 것을 목표로 합니다.

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
- 질문을 통한 선택을 바탕으로 사용자의 독서 취향을 정밀 분석
- 핵심 문장과 클러스터링, 벡터화를 통해 유사한 책들을 함께 추천
- KMeans 클러스터링을 활용하여 비슷한 분위기의 도서 그룹화


⭐️ **LLM을 사용한 감성적 핵심 문장 활용**
- 책의 핵심 문장과 설명을 LLM + RAG를 활용하여 최적화
- 작가의 문체와 감성을 반영한 추천 문장을 생성하여 사용자의 몰입도를 극대화


⭐️ **개인화된 추천 알고리즘**
- Thompson Sampling + KMeans를 결합하여 탐색과 활용 균형 조정
- 사용자 선택 데이터를 기반으로 점진적인 학습을 진행하여 더욱 정교한 추천 제공


⭐️ **데이터 기반 추천 시스템**
- 책 임베딩을 활용하여 코사인 유사도를 기반으로 유사 도서를 추천
- RAG 기법을 활용하여 보다 정밀한 추천 구현


⭐️ **감성적 몰입을 위한 맞춤형 태그 & 편지 형식 추천**
- 추천할 때 단순한 책이 아닌, 사용자에게 보내는 편지 형식으로 감상적인 경험 제공
- 각 책의 핵심 문장과 태그를 함께 추천하여 책의 분위기를 더욱 직관적으로 전달
- 감성적인 접근을 통해 사용자가 책에 대한 기대감을 가질 수 있도록 구성


⭐️ **취향 공유 및 소셜 기능**
- 사용자의 취향을 반영한 추천 결과를 공유하여 독서 경험 확장
- 책 추천을 통해 독서 문화 활성화
<br>

## 2. 개발 환경
| 카테고리 | 기술 스택 |
|:----------:|:----------:|
| **Backend** | FastAPI, PostgreSQL, SQLAlchemy |
| **Frontend** | Flutter |
| **UI/UX** | figma |
| **Recommender Syste & AI** | Python | RAG | LLM | scikit-learn | Thompson Sampling, KMeans Clustering |
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
 ┣  config.py    # DB 초기화 스크립트
?┣  requirements.txt  # 필수 라이브러리 목록
 ┗  README.md
```

<br>

## 4. 개발 기간 및 작업 관리
#### 🗓 개발 기간
- 전체 개발 기간 : 2025-01-06 ~ 2025-02-17
- 데이터베이스 구현 및 알고리즘 설계 : 2025-01-06 ~ 2025-02-03
- API 연동 및 앱,웹 개발 : 2025-02-04 ~ 2025-02-17

#### 🛠 작업 관리
- GitHub & Slack : 진행 상황 공유 및 코드 관리
- Notion : 회의록 정리 및 작업 일정 관리

<br>

## 5. 신경 쓴 부분
- 질문 기반 선택 방식을 도입하여 사용자가 부담 없이 참여하고 필요에 따른 취향을 발견할 수 있도록 설계
- 작가의 문체와 책의 분위기를 데이터화하여 추천 모델에 반영하고, 감성적인 추천 문장을 제공
- 핵심 문장을 벡터화하여 의미적으로 유사한 도서를 추천하고,  정교한 클러스터링 및 톰슨 샘플링을 적용한 최적화된 알고리즘을 구축
- 추천 결과를 편지 형식으로 구성하여 더욱 몰입감 있는 추천 경험을 제공


<br>

## 6. 페이지별 기능
- **메인 페이지 :** 도서 추천 테스트 진입
- **핵심문장 선택 페이지 :** 질문에 답변하여 취향 분석
- **추천 결과 페이지 :** 사용자 취향에 맞는 여러 권의 책 추천
- **책 상세 및 공유 페이지 :** 추천된 책의 정보 및 감성 편지 제공, 공유 가능 기능

<br>

## 📢 프로젝트 후기
#### 👩‍💻 서예은 :

#### 👨‍💻 안효철 : 

#### 🧸 박서현 :

#### 👨‍💻 mentor.최진영 :
