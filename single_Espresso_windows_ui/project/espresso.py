import sys

from PyQt5.QtWidgets import (
  QMainWindow,
  QApplication,
  QPushButton,
  QLineEdit,
  QRadioButton,
  QTableWidget,
  QTableWidgetItem,
  QAction,
  QMenu,
  QFileDialog,
  QLabel,
)
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QFont

from modules.login import Login
from modules.detail import Detail
from modules.local_search import search
from modules.write_json import write_json
from modules.visualization import VzPie, VzWordcloud
from modules.path_gatter import get_img_path
from modules.crawl_progress import Crawler

# 클래스: Espresso
# 기능  : 메인 페이지
class Espresso(QMainWindow):
  def __init__(self) -> None:
    super().__init__()
    self.setFont(QFont("맑은 고딕", 10))
    self.result_list = []
    self.__stopwords = [  # 불용어 리스트
      "방법", "방식", "장치", "복수", "그것", "구비",
      "기반", "이용", "사용", "맞춤", "통해", "통한",
      "상기", "포함", "여부", "요청", "사이", "경우",
      "부분", "각각", "하나", "다수", "개시", "이의",
    ]
    self.conn = Login()  # 로그인창
    self.conn.setFont(QFont("맑은 고딕", 10))
    self.conn.show()
    self.conn.exec_()  # 로그인 완료 될 때까지 다음 코드 실행 보류
    self.user = {
      "id": self.conn.user_id,
      "pw": self.conn.user_pw,
    }
    self.is_crawl_running = False
    if self.conn.patent_db:
      self.init_ui()  # 로그인 끝나면 메인 화면 호출
    else:
      sys.exit()  # 로그인 되지 않은 경우 종료


  # 함수명: set_table_no_result
  # 기능  : 검색결과를 시각화 이미지 또는 JSON 파일 저장할 때
  #        검색결과가 없는 경우 출력할 메시지 set_table 메소드에 전달
  def set_table_no_result(self) -> None:
    self.set_table(txt_list=[
      "",
      "검색결과가 없습니다.",
      "검색결과를 저장하기 위해선 로컬검색이 필요합니다."
    ])


  # 함수명: get_img_name
  # 기능  : 시각화 이미지 파일 저장 경로 획득
  # 반환값: 파일 저장 경로/파일명(str)
  def get_img_name(self) -> str:
    return QFileDialog.getSaveFileName(self, "시각화 파일 저장", "", "Image (*.jpg)")[0]


  # 함수명: save_db_wc
  # 기능  : DB 워드클라우드 시각화
  def save_db_wc(self) -> None:
    img_name = self.get_img_name()
    if img_name:
      VzWordcloud(self.__stopwords, img_name).get_vz_wc(patent_db=self.conn.patent_db)


  # 함수명: save_res_wc
  # 기능  : 검색결과 워드클라우드 시각화
  def save_res_wc(self) -> None:
    if self.result_list:
      img_name = self.get_img_name()
      if img_name:
        VzWordcloud(self.__stopwords, img_name).get_vz_wc(data_list=self.result_list)
    else:
      self.set_table_no_result()


  # 함수명: save_db_pie
  # 기능  : DB 파이그래프 시각화
  def save_db_pie(self) -> None:
    img_name = self.get_img_name()
    if img_name:
      VzPie(img_name).get_vz_pie(patent_db=self.conn.patent_db)


  # 함수명: save_res_pie
  # 기능  : 검색결과 파이그래프 시각화
  def save_res_pie(self) -> None:
    if self.result_list:
      img_name = self.get_img_name()
      if img_name:
        VzPie(img_name).get_vz_pie(data_list=self.result_list)
    else:
      self.set_table_no_result()


  # 함수명: get_json_name
  # 기능  : JSON 파일 저장 경로 획득
  # 반환값: 파일 저장 경로/파일명(str)
  def get_json_name(self) -> str:
    return QFileDialog.getSaveFileName(self, "JSON 파일 저장", "", "JSON (*.json)")[0]


  # 함수명: save_db_json
  # 기능  : DB 데이터 JSON 파일로 저장
  def save_db_json(self) -> None:
    json_name = self.get_json_name()
    if json_name:
      write_json(json_name,patent_db=self.conn.patent_db)


  # 함수명: save_res_json
  # 기능  : 검색결과 JSON 파일로 저장
  def save_res_json(self) -> None:
    if self.result_list:  # 검색결과 저장
      json_name = self.get_json_name()
      if json_name:
        self.result_list.insert(0, {"query":self.query.text()})
        write_json(json_name, data_list=self.result_list)
        self.result_list.pop(0)
    else:
      self.set_table_no_result()


  # 함수명: show_detail
  # 기능  : 로컬 검색결과 상세 정보 출력
  def show_detail(self) -> None:
    if self.result_list:
      idx = self.table.currentIndex().row()
      if not idx:
        return
      data = self.result_list[idx-1]
      self.hide()
      detail = Detail(data)
      detail.show()
      detail.exec_()
      self.show()


  # 함수명: set_button_stat
  # 기능  : 크롤러 실행중일 때 크롤러 버튼 비활성화
  def set_button_stat(self) -> None:
    if self.radio_crawl.isChecked() and self.is_crawl_running:
      self.btn_search.setDisabled(True)
    else:
      self.btn_search.setEnabled(True)


  # 함수명: submit_query
  # 기능  : 검색 버튼 동작
  def submit_query(self) -> None:
    self.result_list.clear()
    search_query = self.query.text()
    if search_query:
      if self.radio_crawl.isChecked():  # 라디오버튼 크롤러 선택 된 경우
        self.is_crawl_running = True
        self.set_button_stat()
        crawler = Crawler(self, search_query, self.user)
        crawler.setFont(QFont("맑은 고딕", 10))
        crawler.show()  # 크롤러 실행
      elif self.radio_search.isChecked():  # 라디오버튼 로컬검색 선택 된 경우
        self.result_list = search(self.conn.patent_db, search_query, self.__stopwords)
        if self.result_list:
          self.set_table(txt_list=self.result_list[:13])
        else:
          self.set_table(txt_list=["","로컬 DB 검색 결과가 없습니다.", "검색어를 확인해 주세요."])
    else:
      self.set_table(txt_list=["","검색어를 입력 하세요."])


  # 함수명: set_table
  # 기능  : 상황에 따라 table 텍스트 설정
  # 입력값: dummy=QRadioButton.clicked 에서 보내는 매개변수(True, 사용 안함) |
  #        txt_list=검색결과 또는 화면에 출력할 문자열이 담긴 리스트
  def set_table(self, dummy:bool=False, txt_list:list[str]=[]) -> None:
    self.set_button_stat()
    self.table.clear()
    if not txt_list:  # 기본 출력
      self.query.clear()
      self.result_list.clear()
      if self.radio_crawl.isChecked():  # 크롤러가 선택 된 경우
        txt_list = txt_list if txt_list else [
          "",
          "현재 선택된 검색기는 KIPRIS Crawler 입니다.",
          "KIPRIS의 검색결과를 크롤링해",
          "사용자의 로컬 데이터베이스에 저장 합니다.",
          "",
          "로컬검색을 원하시면 [F3] 키를 누르거나",
          "검색창 상단의 라디오 버튼을 눌러 변경 하세요.",
          "",
          "",
          "사이트의 데이터 사용량에 따라 진행 양상이 다를 수 있습니다.",
          "오후 2시~6시 사이의 사용을 권장 하지 않습니다."
        ]
      elif self.radio_search.isChecked():  # 로컬검색기가 선택 된 경우
        txt_list = txt_list if txt_list else [
          "",
          "현재 선택된 검색기는 로컬검색기 입니다.",
          "로컬검색 결과는 더블클릭해 상세 정보를 보거나",
          "좌측 상단 메뉴를 통해 저장 할 수 있습니다.",
          "",
          "크롤링을 원하시면 [F2] 키를 누르거나",
          "검색창 상단의 라디오 버튼을 눌러 변경 하세요.",
          "",
          "",
          "문장, 키워드, 출원인, 출원번호를 이용한 검색이 가능합니다."
        ]
    elif type(txt_list[0]) == dict:  # 검색결과 출력
      results = txt_list
      txt_list = [" ───────────────검색결과─────────────── "]
      for i,title in enumerate([result["title"] for result in results]):
        txt_list.append(f'{i+1:2d}. {title}')
    for i,txt in enumerate(txt_list):
      self.table.setItem(i,0,QTableWidgetItem(txt))


  # 함수명: keyPressEvent
  # 기능  : F2, F3 키로 라디오 버튼 스위치
  # 입력값: e=키 입력값
  def keyPressEvent(self, e) -> None:
    if e.key() == 16777265 and not self.radio_crawl.isChecked():  # F2
      self.radio_crawl.setChecked(True)
      self.set_table()
    if e.key() == 16777266 and not self.radio_search.isChecked():  # F3
      self.radio_search.setChecked(True)
      self.set_table()


  # 함수명: init_ui
  # 기능  : 메인 화면 출력
  def init_ui(self) -> None:
    # 전체 버튼 크기(가로, 세로)
    btn_size = QSize(86, 24)

    # 창 크기
    self.setFixedSize(QSize(465,550))

    # 타이틀
    self.setWindowTitle(f'Espresso - {self.user["id"]}')

    # 아이콘
    self.setWindowIcon(QIcon(get_img_path("./images/Espresso.png")))

    # 윈도우 닫기 버튼 비활성화
    self.setWindowFlag(Qt.WindowCloseButtonHint, False)

    # 메뉴바: 시각화, JSON 파일 등 파일저장 관련 기능
    menubar = self.menuBar()  # 메뉴바 생성
    menubar.setStyleSheet("""
      QMenuBar{
        background-color: #E1E1E1;
      }""")
    file_menu = menubar.addMenu("파일")  # 파일 메뉴 추가

    # 데이터베이스 관련 저장 기능
    menu_db = QMenu("데이터베이스", self)
    menu_db_json = QAction("JSON 파일 저장", self)
    menu_db_json.triggered.connect(self.save_db_json)
    menu_db_wc = QAction("워드클라우드", self)
    menu_db_wc.triggered.connect(self.save_db_wc)
    menu_db_pie = QAction("파이그래프", self)
    menu_db_pie.triggered.connect(self.save_db_pie)
    menu_db.addAction(menu_db_json)
    menu_db.addAction(menu_db_wc)
    menu_db.addAction(menu_db_pie)

    # 검색결과 관련 저장 기능
    menu_result = QMenu("검색결과", self)
    menu_result_json = QAction("JSON 파일 저장", self)
    menu_result_json.triggered.connect(self.save_res_json)
    menu_result_wc = QAction("워드클라우드", self)
    menu_result_wc.triggered.connect(self.save_res_wc)
    menu_result_pie = QAction("파이그래프", self)
    menu_result_pie.triggered.connect(self.save_res_pie)
    menu_result.addAction(menu_result_json)
    menu_result.addAction(menu_result_wc)
    menu_result.addAction(menu_result_pie)

    # 메뉴바에 기능 추가
    file_menu.addMenu(menu_db)
    file_menu.addMenu(menu_result)

    # 검색 라디오 버튼 [크롤링|내부검색]
    self.radio_crawl = QRadioButton("크롤링", self)
    self.radio_crawl.move(12,25)  # 라디오 버튼 위치
    self.radio_crawl.setChecked(True)  # 기본으로 크롤링 선택
    self.radio_crawl.clicked.connect(self.set_table)
    self.radio_search = QRadioButton("로컬검색", self)
    self.radio_search.move(90,25)  # 라디오 버튼 위치
    self.radio_search.clicked.connect(self.set_table)

    # 검색어 입력창
    self.query = QLineEdit("",self)
    self.query.move(10,51)  # 검색창 위치
    self.query.resize(QSize(359,22))  # 검색창 크기
    self.query.setFocus()  # 프로그램 열릴 때 커서 위치
    self.query.returnPressed.connect(self.submit_query)  # Enter 입력으로 검색 실행

    # 검색 버튼
    self.btn_search = QPushButton("검색", self)
    self.btn_search.move(369,50)  # 버튼 위치
    self.btn_search.resize(btn_size)  # 버튼 크기
    self.btn_search.clicked.connect(self.submit_query)  # 버튼 클릭으로 검색 실행

    # 안내 및 검색결과 출력 공간
    self.table = QTableWidget(self)
    self.table.resize(QSize(445,422))  # 크기
    self.table.move(10,85)  # 위치
    self.table.setRowCount(14)  # 세로 길이 지정
    self.table.setColumnCount(1)  # 가로 길이 지정
    self.table.setColumnWidth(0, 445)  # 0번 컬럼 너비
    self.table.verticalHeader().hide()  # row(세로) 번호 숨기기
    self.table.horizontalHeader().hide()  # column(가로) 번호 숨기기
    self.table.setShowGrid(False)  # 구분선 숨기기
    self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 수정 트리거 제거
    self.table.doubleClicked.connect(self.show_detail)
    self.table.setStyleSheet("""
    QTableWidget{
      outline: 0;
    }
    QTableWidget::item{
      padding: 7px;
      background-color: #fff;
    }
    QTableWidget::item:selected{
      background-color: #ffc;
      color: #000;
    }""")  # 테이블 스타일 지정
    self.set_table()

    # 프로그램 정보
    info_txt = "Espresso WinUI ver 1.1.7\nProgramed by Hugo(h900506@gmail.com)"
    program_info = QLabel(info_txt, self)
    program_info.move(10,511)
    program_info.resize(QSize(400,35))

    # 프로그램 종료 버튼
    btn_quit = QPushButton("종료", self)
    btn_quit.move(369,515)  # 버튼 위치
    btn_quit.resize(btn_size)  # 버튼 크기
    btn_quit.clicked.connect(sys.exit)  # 프로그램 종료



app = QApplication(sys.argv)
ui_main = Espresso()
ui_main.show()
sys.exit(app.exec_())
