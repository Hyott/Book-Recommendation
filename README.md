## Project Member
## Google Drive URL :
https://drive.google.com/drive/folders/1Fwagsc1JuDP8kbqkDSTzfTQXWDvehur-?usp=sharing


### Team
| Name          | Role                   | GitHub Profile                              | Key Contributions               |
|---------------|------------------------|---------------------------------------------|----------------------------------|
| **Hyocheol Ahn** | 추후작성        | [@Hyott](https://github.com/Hyott)    | 추후작성 |
| **Yeeun Seo**    | 추후작성        | [@seo9045](https://github.com/seo9045)| 추후작성 |
| **Seohyeon**     | 추후작성        | [@heabppi](https://github.com/heabppi)| 추후작성 |

### Special Thanks
- **Mentor:** [JinYeong Choi](https://www.linkedin.com/in/jin0choi/)


## Git Commit Message Convention
프로젝트의 Git 커밋 메시지는 일관성을 유지하기 위해 다음과 같은 헤더를 사용합니다. 이 규칙을 따르면 커밋의 목적을 명확히 알 수 있어 협업과 코드 리뷰가 더 효율적입니다.

| **헤더**    | **의미**                                                                                   | **예시**                                     |
|-------------|--------------------------------------------------------------------------------------------|---------------------------------------------|
| `feat`      | 새로운 기능 추가                                                                           | `feat: Add user login feature`             |
| `fix`       | 버그 수정                                                                                  | `fix: Correct null pointer error`          |
| `docs`      | 문서 추가 또는 수정 (README, 코드 주석 등)                                                  | `docs: Update README for installation`     |
| `style`     | 코드 스타일 변경 (기능에는 영향 없음, 예: 포매팅, 공백 추가 등)                              | `style: Format code with black`            |
| `refactor`  | 코드 리팩토링 (기능 변경 없이 구조 개선)                                                    | `refactor: Simplify book parsing logic`    |
| `test`      | 테스트 코드 추가 또는 수정                                                                  | `test: Add unit tests for API endpoints`   |


### 커밋 메시지 작성 규칙

1. **헤더**는 소문자로 작성하며, 한 칸 띄운 뒤 콜론(`:`)과 공백을 추가합니다.
   - 예: `feat: Add user login feature`
2. **헤더는 간결하고 명확하게** 작성합니다.
   - 50자 이내로 작성.
3. **명령형 동사**를 사용하여 커밋 의도를 명확히 합니다.
   - 예: `추가`, `수정`, `업데이트` 등.



# 📚 Read4U (책 큐레이션 서비스 앱)

## 📌 프로젝트 소개
Read4U는 사용자의 독서 취향을 정밀하게 분석하여 맞춤형 에세이 도서를 추천하는 인공지능 기반 북 큐레이션 서비스 앱입니다. 
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

## 🎖 Special Thanks
- **Mentor:** [JinYeong Choi](https://www.linkedin.com/in/jin0choi/)


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
- Thompson Sampling을 활용한 탐색-활용 균형 조정
- 사용자 선택 데이터를 기반으로 점진적 학습을 진행하여 더욱 정교한 추천 제공

⭐️ **데이터 기반 추천 시스템**
- 책 임베딩을 활용하여 코사인 유사도를 기반으로 유사 도서를 추천
- RAG(Retrieval-Augmented Generation) 기법을 활용하여 보다 정밀한 추천 구현

<br>

## 2. 개발 환경
| 카테고리 | 기술 스택 |
|:----------:|:----------:|
| **Backend** | FastAPI, PostgreSQL |
| **Frontend** | Flutter, figma |
| **ML/NLP** | Hugging Face Transformers, TensorFlow/Keras, PyTorch |
| **검색 및 벡터화** | RAG |
| **배포** | Docker|
| **운영체제** | Windows, macOS, Linux |
| **Communication** | Git, Slack, Notion|


## 3. 설치 방법 및 실행 가이드
### 1️⃣ 가상 환경 설정 및 패키지 설치
```bash
python -m venv venv
source venv/bin/activate  # (Windows의 경우 venv\Scripts\activate)
pip install -r requirements.txt
```

### 2️⃣ 데이터베이스 초기화
```bash
python init_db.py
```

### 3️⃣ 서버 실행
```bash
uvicorn main:app --reload
```

## 4. 프로젝트 구조
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

## 5. (주) 역할 분담

#### 👩‍💻 서예은 : API 연동 및 Flutter 구현, UI/UX 디자인(Figma)

#### 👨‍💻 안효철 : 추천 알고리즘 구현, LLM 및 벡터화를 활용한 추천 시스템 개발

#### 🧸 박서현 : API 구현 및 데이터베이스 설계, PM

<br>

## 6. 개발 기간 및 작업 관리
#### 🗓 개발 기간
- 전체 개발 기간 : 2025-01-06 ~ 2025-02-17
- 데이터베이스 구현 및 알고리즘 설계 : 2025-01-06 ~ 2025-02-03
- API 연동 및 앱 개발 : 2025-02-04 ~ 2025-02-17

#### 🛠 작업 관리
- GitHub & Slack : 진행 상황 공유 및 코드 관리
- Notion : 회의록 정리 및 작업 일정 관리

<br>

## 7. 신경 쓴 부분
- 사용자가 쉽게 참여할 수 있고 몰입감 있는 취향 분석 테스트 설계
- 개인화된 맞춤 도서 추천 알고리즘 개발
- 벡터화된 핵심 문장 기반의 정밀한 추천 시스템 구현

<br>

## 8. 페이지별 기능
- **메인 페이지 :** 도서 추천 테스트 진입
- **테스트 페이지 :** 질문에 답변하여 취향 분석
- **추천 결과 페이지 :** 사용자 취향에 맞는 여러 권의 책 추천
- **책 상세 및 공유 페이지 :** 추천된 책의 정보 및 리뷰 제공, 공유 가능 기능

<br>

##  9. 트러블 슈팅
### 1️⃣ 데이터베이스 오류 해결
**문제:** `오류` 발생
**해결:** 데이터베이스 초기화 스크립트를 실행하세요.
```bash
python init_db.py
```

### 2️⃣ 가상 환경 오류 해결
**문제:** `오류`
**해결:** 가상 환경이 활성화되지 않았을 수 있습니다. 아래 명령어를 실행하세요.
```bash
source venv/bin/activate  # (Windows의 경우 venv\Scripts\activate)
```

<br>

##  10. 개선 목표
- [ ] AWS를 사용하여 주기적인 에세이 업로드
- [ ] 공유 기능 업데이트(더 다양한 플랫폼으로 연동 가능하게)
- [ ] UI/UX 최적화 및 macOS 앱 배포


## 📢 프로젝트 후기
#### 👩‍💻 서예은 :

#### 👨‍💻 안효철 : 

#### 🧸 박서현 : 
