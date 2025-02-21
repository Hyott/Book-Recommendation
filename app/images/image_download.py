# 이미지 다운로드
import os
import json
import urllib.request

# 현재 실행 중인 파일의 경로 (image_download.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# JSON 파일 상대 경로 설정
JSON_FILE_PATH = os.path.join(BASE_DIR, "../../data/scraping/filtered_book_unique.json")

# 다운로드 폴더 상대 경로 설정
SAVE_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(SAVE_DIR, exist_ok=True)  # 저장 폴더 생성


def download_image(isbn, url):
    """이미지 URL을 받아 다운로드하고 저장"""
    filename = f"{isbn}.jpg"  # ISBN을 파일명으로 저장
    file_path = os.path.join(SAVE_DIR, filename)

    try:
        urllib.request.urlretrieve(url, file_path)  # 이미지 다운로드 및 저장
        print(f"✅ 다운로드 완료: {file_path}")
        return file_path
    except Exception as e:
        print(f"❌ 다운로드 실패: {url} | 오류: {e}")
        return None


def process_json_and_download():
    """JSON 파일에서 isbn과 img_url을 추출하여 이미지 다운로드"""
    try:
        # JSON 파일 열기
        with open(JSON_FILE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)

        # 각 항목에서 isbn과 img_url 추출 후 다운로드 실행
        for book in data:
            isbn = book.get("isbn")
            img_url = book.get("img_url")

            if isbn and img_url:  # 값이 존재하는 경우만 다운로드
                download_image(isbn, img_url)
            else:
                print(f"❗️ 이미지 URL 없음: {book.get('title')}")

    except Exception as e:
        print(f"❌ JSON 파일 처리 오류: {e}")


# ✅ 실행
if __name__ == "__main__":
    process_json_and_download()



# # 이미지 다운로드(거꾸로)
# import os
# import json
# import urllib.request

# # 현재 실행 중인 파일의 경로 (image_download.py)
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# # JSON 파일 상대 경로 설정
# JSON_FILE_PATH = os.path.join(BASE_DIR, "../../data/scraping/filtered_book_unique.json")

# # 다운로드 폴더 상대 경로 설정
# SAVE_DIR = os.path.join(BASE_DIR, "downloads")
# os.makedirs(SAVE_DIR, exist_ok=True)  # 저장 폴더 생성


# def download_image(isbn, url):
#     """이미지 URL을 받아 다운로드하고 저장"""
#     filename = f"{isbn}.jpg"  # ISBN을 파일명으로 저장
#     file_path = os.path.join(SAVE_DIR, filename)

#     # ✅ 이미 다운로드된 파일이 있으면 스킵
#     if os.path.exists(file_path):
#         print(f"✅ 이미 존재하는 파일: {file_path} (다운로드 생략)")
#         return None

#     try:
#         urllib.request.urlretrieve(url, file_path)  # 이미지 다운로드 및 저장
#         print(f"✅ 다운로드 완료: {file_path}")
#         return file_path
#     except Exception as e:
#         print(f"❌ 다운로드 실패: {url} | 오류: {e}")
#         return None


# def process_json_and_download():
#     """JSON 파일에서 isbn과 img_url을 추출하여 이미지 다운로드"""
#     try:
#         # JSON 파일 열기
#         with open(JSON_FILE_PATH, "r", encoding="utf-8") as file:
#             data = json.load(file)

#         # ✅ 끝에서부터 JSON 데이터 순회
#         for book in reversed(data):
#             isbn = book.get("isbn")
#             img_url = book.get("img_url")
#             file_path = os.path.join(SAVE_DIR, f"{isbn}.jpg")

#             # ✅ 파일이 이미 존재하면 즉시 종료
#             if os.path.exists(file_path):
#                 print(f"✅ 기존 파일 발견: {file_path} → 다운로드 중단")
#                 break

#             # ✅ 이미지 다운로드 진행
#             if isbn and img_url:
#                 download_image(isbn, img_url)
#             else:
#                 print(f"❗️ 이미지 URL 없음: {book.get('title')}")

#     except Exception as e:
#         print(f"❌ JSON 파일 처리 오류: {e}")


# # ✅ 실행
# if __name__ == "__main__":
#     process_json_and_download()