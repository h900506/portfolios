import sys

from PyQt5.QtWidgets import (
  QApplication,
  QDialog,
  QPushButton,
  QTableWidget,
  QTableWidgetItem,
  QHeaderView,
)
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon

from modules.path_gatter import get_img_path

# 클래스: Detail
# 기능  : 로컬 검색결과 출력 페이지
# 입력값: data=상세정보 출력할 값
class Detail(QDialog):
  def __init__(self, data:dict) -> None:
    super().__init__()
    self.data = {
      "title": data["title"],
      "application_number": data["application_number"],
      "applicant": data["applicant"],
      "cpc": "\n".join(data["cpc"]),
      "keywords": ", ".join(data["keywords"]),
      "summary": data["summary"],
    }
    self.init_ui()

  # 함수명: init_ui
  # 기능  : 디테일 화면 출력
  def init_ui(self) -> None:
    # 창 크기
    self.setFixedSize(QSize(800,800))

    # 타이틀
    self.setWindowTitle("Espresso Login")

    # 아이콘
    self.setWindowIcon(QIcon(get_img_path("./images/Espresso.png")))

    # 윈도우 닫기 버튼, ? 비활성화
    self.setWindowFlag(Qt.WindowCloseButtonHint, False)
    self.setWindowFlag(Qt.WindowContextHelpButtonHint , False)

    # 상세정보 테이블
    table = QTableWidget(self)
    table.setRowCount(6)  # 세로 길이 지정
    table.setColumnCount(2)  # 가로 길이 지정
    table.move(30,30)  # 위치
    table.resize(QSize(740, 700))  # 크기
    table.setColumnWidth(0, 100)  # 0번 컬럼 너비
    table.verticalHeader().hide()  # row(세로) 번호 숨기기
    table.horizontalHeader().hide()  # column(가로) 번호 숨기기
    table.setEditTriggers(QTableWidget.NoEditTriggers)  # 수정 트리거 제거
    table.horizontalHeader().setStretchLastSection(True)  # 마지막 컬럼 너비(화면에 맞게 확장)
    table.verticalHeader().setStretchLastSection(True)  # 마지막 컬럼 높이(화면에 맞게 확장)
    kor_keys = ["제목", "출원번호", "출원인", "CPC", "키워드" , "요약"]  # 화면에 표시할 한글 키
    eng_keys = ["title", "application_number", "applicant", "cpc", "keywords", "summary"]  # data에 사용된 영어 키
    for i in range(6):
      table.setItem(i,0,QTableWidgetItem(kor_keys[i]))  # 한글 키 출력
      table.setItem(i,1,QTableWidgetItem(self.data[eng_keys[i]]))  # 값 출력
      table.item(i,0).setTextAlignment(Qt.AlignTop)  # 줄바꿈 생기는 값을 위해 상단 정렬
      table.item(i,1).setTextAlignment(Qt.AlignTop)
      if i < 5:
        table.verticalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)  # 컨텐츠에 맞게 테이블 크기 확장(마지막 row 제외)
    table.setStyleSheet("""
    QTableWidget {
      outline: 0;
    }
    QTableWidget::item {
      padding: 7px;
      background-color: #fff;
    }
    QTableWidget::item:selected{
      background-color: #fff;
      color: #000;
    }""")  # 테이블 스타일 지정


    # 디테일 닫기 버튼
    btn_quit = QPushButton("닫기", self)
    btn_quit.move(700, 755)  # 버튼 위치
    btn_quit.resize(QSize(86, 24))  # 버튼 크기
    btn_quit.clicked.connect(self.close)  # 디테일 닫기



app = QApplication(sys.argv)
