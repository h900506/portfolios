import sys
from pymysql import OperationalError

from PyQt5.QtWidgets import (
  QApplication,
  QDialog,
  QPushButton,
  QLineEdit,
  QLabel,
)
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon

from modules.patent_db import PatentDB
from modules.path_gatter import get_img_path
from modules.control_password import encryption

# 클래스: Login
# 기능  : 로그인 페이지
class Login(QDialog):
  def __init__(self) -> None:
    super().__init__()
    self.init_ui()
    self.user_id = ""
    self.user_pw = ""
    self.patent_db = None


  # 함수명: submit_user
  # 기능  : 로그인 버튼 동작, db커넥터 생성
  def submit_user(self) -> None:
    if not self.user_id:
      self.alert.setText("아이디를 입력 하세요.")
    elif not self.user_pw:
      self.alert.setText("비밀번호를 입력 하세요.")
    elif self.user_id and self.user_pw:
      try:
        patent_db = PatentDB({"id":self.user_id, "pw":self.user_pw})
      except OperationalError:
        self.alert.setText("계정이 올바르지 않습니다.\n계정을 확인 해 주세요.")
      else:
        self.user_pw = encryption(self.user_pw)
        self.patent_db = patent_db
        self.close()


  # 함수명: set_uid, set_upw
  # 기능  : 입력 받은 계정 정보 self.__user로 전달
  # 입력값: 사용자가 입력한 로컬 데이터베이스의 id, password
  def set_uid(self, txt:str) -> None:
    self.user_id = txt
  def set_upw(self, txt:str) -> None:
    self.user_pw = txt



  # 함수명: init_ui
  # 기능  : 로그인 화면 출력
  def init_ui(self) -> None:
    # 창 크기
    self.setFixedSize(QSize(300,210))

    # 타이틀
    self.setWindowTitle("Espresso Login")

    # 아이콘
    self.setWindowIcon(QIcon(get_img_path("./images/Espresso.png")))

    # 윈도우 닫기 버튼, ? 버튼 비활성화
    self.setWindowFlag(Qt.WindowCloseButtonHint, False)
    self.setWindowFlag(Qt.WindowContextHelpButtonHint , False)

    # 안내 메시지
    txt = "우리 프로그램을 사용하려면\n로컬 MySql 에 로그인 해야 합니다."
    msg = QLabel(txt, self)
    msg.move(0,15)
    msg.resize(QSize(300, 50))
    msg.setAlignment(Qt.AlignCenter)

    # 로그인 alert
    self.alert = QLabel("", self)
    self.alert.move(0,150)
    self.alert.resize(QSize(200, 50))
    self.alert.setAlignment(Qt.AlignCenter)

    # id 입력창
    uid = QLineEdit("",self)
    uid.move(28, 72)  # id 위치
    uid.resize(QSize(150, 28))  # id 크기
    uid.setPlaceholderText("ID")
    uid.textChanged.connect(self.set_uid)  # id 입력 감지
    uid.returnPressed.connect(self.submit_user)  # Enter 입력으로 로그인

    # pw 입력창
    upw = QLineEdit("",self)
    upw.move(28, 110)  # pw 위치
    upw.resize(QSize(150, 28))  # pw 크기
    upw.setPlaceholderText("PASSWORD")
    upw.setEchoMode(QLineEdit.Password)  # 비밀번호 ●●● 로 보여주기
    upw.textChanged.connect(self.set_upw)  # pw 입력 감지
    upw.returnPressed.connect(self.submit_user)  # Enter 입력으로 로그인

    # 로그인 버튼
    btn_search = QPushButton("로그인", self)
    btn_search.move(200, 70)  # 버튼 위치
    btn_search.resize(QSize(75,72))  # 버튼 크기
    btn_search.clicked.connect(self.submit_user)  # 버튼 클릭으로 로그인

    # 프로그램 종료 버튼
    btn_quit = QPushButton("종료", self)
    btn_quit.move(200, 160)  # 버튼 위치
    btn_quit.resize(QSize(75, 25))  # 버튼 크기
    btn_quit.clicked.connect(sys.exit)  # 프로그램 종료



app = QApplication(sys.argv)
