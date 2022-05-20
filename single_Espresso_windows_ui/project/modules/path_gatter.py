import sys, os

# 함수명: get_img_path
# 기능  : (pyinstaller의 임시폴더 포함)이미지 경로에 접근
# 입력값: img_path=이미지 이름
# 반환값: 이미지 경로
def get_img_path(img_path:str) -> str:
  try:
    base_path = sys._MEIPASS
  except Exception:
    base_path = os.path.abspath(".")
  return os.path.join(base_path, img_path)
