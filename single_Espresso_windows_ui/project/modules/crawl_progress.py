import sys

from PyQt5.QtWidgets import(
  QProgressBar,
  QApplication,
  QBoxLayout,
  QLabel,
  QDialog,
  QPushButton,
  QToolTip,
)
from PyQt5.QtCore import QThread, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By  # find_element_by* 대신 사용
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait  # sleep 대신 사용
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service  # DeprecationWarning 해결
from selenium.common.exceptions import (
  NoSuchElementException,
  StaleElementReferenceException,
  TimeoutException,
  UnexpectedAlertPresentException,
)  # 셀레니움 예외
from webdriver_manager.chrome import ChromeDriverManager  # 최신드라이버 체크&업데이트

from modules.path_gatter import get_img_path
from modules.control_password import decryption
from modules.patent_db import PatentDB

# 클래스: CrawlThread
# 기능  : 크롤러 쓰레드 생성
# 입력값: parent=상위 인스턴스(프로그래스바) | query=검색어 | patent_db=DB커넥터
class CrawlThread(QThread):
  total_count_signal = pyqtSignal(int)
  crawled_count_signal = pyqtSignal(int)
  limit_signal = pyqtSignal(int)
  result_signal = pyqtSignal(bool)
  def __init__(self, parent:object, query:str, patent_db:object) -> None:
    super().__init__(parent)
    self.query = query
    self.patent_db = patent_db
    self.total_count = 0
    self.crawled_count = 0
    self.is_running = True


  # 함수명: crawl_page
  # 기능  : 상세 페이지 크롤링 후 데이터베이스에 입력
  # 입력값: driver=웹드라이버
  def crawl_page(self, driver:webdriver) -> None:
    iframe = WebDriverWait(driver, 60).until(lambda tag: tag.find_element(By.TAG_NAME, "iframe"))
    driver.switch_to.frame(iframe)  # iframe 으로 드라이버 전환

    # 각 태그들이 로드 될 때까지 대기
    WebDriverWait(driver, 60).until(lambda tag: tag.find_element(By.CSS_SELECTOR, "span#apttl"))
    WebDriverWait(driver, 60).until(lambda tag: tag.find_element(By.TAG_NAME, "p"))
    WebDriverWait(driver, 60).until(lambda tag: tag.find_element(By.CSS_SELECTOR, "ul li:nth-of-type(2) span"))
    WebDriverWait(driver, 60).until(lambda tag: tag.find_element(By.CSS_SELECTOR, "ul li:nth-of-type(3)"))
    WebDriverWait(driver, 60).until(lambda tag: tag.find_element(By.CSS_SELECTOR, "ul li:nth-of-type(4) span"))

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    content_list = soup.find("ul")

    # 출원번호
    application_number = content_list.select_one("ul>li:nth-of-type(3)").get_text().replace("(국제)", "").replace("(21) 출원번호/일자", "").split("(")[0].strip()

    # 제목
    title = soup.find("span", id="apttl").get_text().replace('"', "").replace("'", "")

    # 출원인
    applicant = str(content_list.select_one("ul>li:nth-of-type(4)>span")).replace("<br/>", "|").replace("<span>", "").replace("</span>", "").strip().replace(" ", "").replace('"', "").replace("'", "")

    # 요약
    summary = " ".join(map(lambda tag: tag.get_text(), soup.find_all("p"))).replace('"', "").replace("'", "").replace("\t", " ")

    data = {
      "application_number": application_number,
      "title": title,
      "applicant": applicant,
      "summary": summary,
    }

    # CPC
    cpc_list = list(map(lambda x: x[:-9], content_list.select_one("ul>li:nth-of-type(2)>span").get_text().strip().split("\n")))

    # DB 저장
    self.patent_db.insert_db("patents", data)
    for cpc in cpc_list:
      if cpc:
        self.patent_db.insert_db("cpc", {"application_number":application_number,"cpc":cpc})
    self.patent_db.insert_db("keywords", {"application_number":application_number,"keyword":self.query})

    driver.switch_to.default_content()  # 기존 페이지로 드라이버 전환


  # 함수명: ctrl_driver
  # 기능  : 드라이버를 사용해 검색 결과 페이지 조작
  # 입력값: driver=웹드라이버
  def ctrl_driver(self, driver:webdriver) -> None:
    # [{출원번호:"00",검색어:"ㅇㅇ"}] 형태에서 {출원번호:[검색어, 검색어, ...]} 형태로 변환
    patent_keywords = {}
    for dict in self.patent_db.select_db(table="keywords"):
      app_num = dict["application_number"]
      if not app_num in patent_keywords:
        patent_keywords[app_num] = [dict["keyword"]]
      else:
        patent_keywords[app_num].append(dict["keyword"])

    cnt = 0  # while문 제어를 위한 카운트
    cnt_sync = 0
    is_synced = False  # 함수가 재 실행 된 경우 싱크를 맞추기 위한 boolean 값

    # 크롤링 시작
    try:
      WebDriverWait(driver, 5, ignored_exceptions=[StaleElementReferenceException, NoSuchElementException])\
        .until(EC.staleness_of(driver.find_element(By.CSS_SELECTOR, "div.search_section_title > h1 > a:nth-child(2)")))
    except TimeoutException:
      pass  # 최대 5초 기다리지만 에러는 띄우지 않음
    limit_num = int(self.driver.find_element(By.CLASS_NAME, "total").text.replace(",", ""))
    self.limit_signal.emit(limit_num)  # 페이지 전환 되기 전에 실행되는 경우가 있어서 최대한 뒤에 배치

    driver.find_element(By.CSS_SELECTOR, "div.search_section_title > h1 > a:nth-child(2)").click()
    driver.switch_to.window(driver.window_handles[-1])  # 새로 열린 페이지로 드라이버 전환

    while cnt < 630 and self.is_running:  # 페이지 반복문(크롤링 630개(7페이지) 완료 후 브라우저 재 실행)
      try:
        WebDriverWait(driver, 5, ignored_exceptions=[StaleElementReferenceException, NoSuchElementException])\
        .until(EC.staleness_of(driver.find_element(By.CSS_SELECTOR, "#divBiblioLeft > div.snavigation > div > ul a")))
      except TimeoutException:
        pass  # 최대 5초 기다리지만 에러는 띄우지 않음
      except (NoSuchElementException, AttributeError):
        continue  # 재시도
      except UnexpectedAlertPresentException as e:
        print("\n\n\n? 이게 뭐람 11111\n\n\n")
        print(e) #! 예외 1차 발생 후 재 확인이 안됨 - 얼럿창 팝업 후 바로 브라우저 종료 되는 현상(아마도 에러 발생으로 브라우저 종료)
        continue
      try:
        link_list = driver.find_elements(By.CSS_SELECTOR, "#divBiblioLeft > div.snavigation > div > ul a")
      except UnexpectedAlertPresentException as e:
        print("\n\n\n? 이게 뭐람 22222\n\n\n")
        print(e) #! 예외 1차 발생 후 재 확인이 안됨 - 얼럿창 팝업 후 바로 브라우저 종료 되는 현상(아마도 에러 발생으로 브라우저 종료)
        continue
      for idx,link in enumerate(link_list):  # 페이지 내 특허 리스트 반복문
        if not self.is_running:
          break
        try:
          app_num = link.text.replace("-","")
        except StaleElementReferenceException:
          driver.quit()
          return True
        if not app_num in patent_keywords:  # DB에 저장되지 않은 특허인 경우 크롤
          if idx:  # 반복문의 첫 번째 특허를 크롤링 할 경우 클릭 없이 바로 실행
            link.click()
          self.crawl_page(driver)  # 크롤 함수 호출
          cnt += 1
          self.crawled_count += 1
          self.crawled_count_signal.emit(self.crawled_count)
        elif not self.query in patent_keywords[app_num]:  # 기존 DB에 저장된 특허가 다른 검색어로 검색 되었을 때 검색어 추가
          self.patent_db.insert_db("keywords", {"application_number":app_num, "keyword":self.query})

        if cnt_sync == self.total_count:
          is_synced = True
        if is_synced:
          self.total_count += 1
        else:
          cnt_sync += 1

        self.total_count_signal.emit(self.total_count)

      # 페이지 넘기기
      if self.is_running:
        try:
          page_link = driver.find_element(By.CSS_SELECTOR, "#divBiblioLeft > div.board_pager02 > strong + a")
        except NoSuchElementException:  # 다음 페이지가 없는 경우(마지막 페이지)
          driver.quit()
          return False
        else:  # 다음 페이지로 이동
          page_link.click()
      else:
        driver.quit()
        return False

    driver.quit()  # 브라우저, 프로세스 종료
    return True


  # 함수명: get_driver
  # 기능  : 웹드라이버 다운로드 및 옵션 적용 후 반환
  # 반환값: driver=웹드라이버
  def get_driver(self) -> webdriver:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_argument("--incognito")  # 동일 조건 실행, 캐시 삭제 하기 위한 시크릿모드
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver


  # 함수명: run (.start()로 실행되는 메소드)
  # 기능  : KIPRIS 사이트 접속 후 검색
  def run(self) -> None:
    self.driver = self.get_driver()
    self.driver.get("http://kpat.kipris.or.kr/kpat/searchLogina.do?next=MainSearch")
    while True:
      try:
        for i in range(2, 7):  # 공개, 등록만 검색
          self.driver.find_element(By.CSS_SELECTOR, f'input#leftHangjung0{i}').click()
      except(StaleElementReferenceException, NoSuchElementException):
        continue
      else:
        # self.driver.find_element(By.CSS_SELECTOR, "span.btn_ok>a>img").click()
        self.driver.find_element(By.ID, "queryText").send_keys(self.query)
        self.driver.find_element(By.CLASS_NAME, "input_btn").click()
        WebDriverWait(self.driver, 60).until(EC.invisibility_of_element((By.ID, "loadingBarBack")))
        Select(self.driver.find_element(By.ID, "opt28")).select_by_value('90')  # 90개씩 보기
        self.driver.find_element(By.CSS_SELECTOR, "div#pageSel>a>img").click()
        break
    try:
      self.driver.find_element(By.CLASS_NAME, "search_nodata")
    except NoSuchElementException:
      if self.ctrl_driver(self.driver):  # 검색 완료 후 컨트롤 함수 호출
        return self.run()  # 브라우저 램 부족현상 회피하기 위해 630개(7페이지)마다 크롤러 재 실행
      else:  # 크롤링 완료 또는 중지
        self.result_signal.emit(False)
        self.driver.quit()
        self.patent_db.close_db()
        self.quit()
    else:  # 검색 결과가 없는 경우
      self.result_signal.emit(True)
      self.driver.quit()



# 클래스: SignalChecker
# 기능  : 쓰레드의 신호를 받아 작동하는 함수 모음
# 입력값: parent=상위 인스턴스(프로그레스바) | grandpa=최상위 인스턴스(메인화면)
class SignalChecker:
  def __init__(self, parent:object, grandpa:object) -> None:
    self.parent = parent
    self.grandpa = grandpa


  # 함수명: check_result
  # 기능  : 크롤링 종료 후 결과 출력
  # 입력값: res=쓰레드에서 넘어온 크롤링 결과(True:검색결과 없음, False:크롤링 완료)
  def check_result(self, res:bool) -> None:
    if res:  # 검색 결과가 없는 경우
      self.parent.main_msg.setText("검색 결과가 없습니다.\n검색어를 확인 해주세요.")
      self.parent.progress_bar.hide()
    else:  # 크롤링 완료
      crawled_result = self.parent.crawled_msg.text().split("\n")[1]
      self.parent.crawled_msg.clear()
      self.parent.count_msg.clear()
      self.parent.limit_msg.clear()
      self.parent.main_msg.setText(f'{crawled_result}건의 크롤링이 완료 되었습니다.')
      self.parent.btn_quit.setText("닫기")
    self.parent.btn_quit.setEnabled(True)


  # 함수명: set_limit
  # 기능  : 검색결과 갯수 출력
  # 입력값: n=쓰레드에서 넘어온 검색결과 갯수
  def set_limit(self, n:int) -> None:
    self.parent.main_msg.clear()
    if not self.parent.count_msg.text():
      self.parent.count_msg.setText("0")
    if not self.parent.crawled_msg.text():
      self.parent.crawled_msg.setText("crawled\n0")
    self.parent.limit_msg.setText(f' / {n}')
    self.parent.progress_bar.setMaximum(n)
    self.parent.btn_quit.setEnabled(True)


  # 함수명: set_count
  # 기능  : 확인한 전체 특허정보 갯수 출력
  # 입력값: n=쓰레드에서 넘어온 특허정보 갯수
  def set_count(self, n:int) -> None:
    self.parent.main_msg.clear()
    self.parent.count_msg.setText(str(n))


  # 함수명: set_crawled
  # 기능  : 크롤링 한 특허정보 갯수 출력
  # 입력값: n=쓰레드에서 넘어온 특허정보 갯수
  def set_crawled(self, n:int) -> None:
    self.parent.main_msg.clear()
    self.parent.crawled_msg.setText(f'crawled\n{n}')



# 클래스: Crawler
# 기능  : 크롤러 화면(프로그레스바)
# 입력값: parent=상위 인스턴스(메인화면) | query=검색어 | user=유저 계정 정보
class Crawler(QDialog):
  def __init__(self, parent:object, query:str, user:dict) -> None:
    super().__init__(parent)
    self.parent = parent
    self.sc = SignalChecker(self, parent)
    self.__user = {
      "id": user["id"],
      "pw": decryption(user["pw"])
    }
    self.patent_db = PatentDB(self.__user, ischecked=True)
    self.crawl_thread = CrawlThread(self, query, self.patent_db)
    self.init_ui()
    self.crawl_thread.start()


  # 함수명: close_crawler
  # 기능  : 크롤링 중단 종료 후 크롤러 버튼 활성화
  def close_crawler(self) -> None:
    if self.crawl_thread.is_running:
      self.crawl_thread.is_running = False
    self.parent.is_crawl_running = False
    self.parent.set_button_stat()
    self.close()


  # 함수명: init_ui
  # 기능  : 크롤러 화면(프로그레스바) 출력
  def init_ui(self) -> None:
    # 창 크기
    self.setFixedSize(QSize(300,100))

    # 타이틀
    self.setWindowTitle("Espresso Crawler")

    # 아이콘
    self.setWindowIcon(QIcon(get_img_path("./images/Espresso.png")))

    # 윈도우 닫기 버튼, ? 버튼 비활성화, 항상 위에 표시
    self.setWindowFlag(Qt.WindowCloseButtonHint, False)
    self.setWindowFlag(Qt.WindowContextHelpButtonHint , False)
    self.setWindowFlag(Qt.WindowStaysOnTopHint)

    # 크롤링 시작, 종료 메시지
    self.main_msg = QLabel("크롤링을 시작 합니다.", self)
    self.main_msg.resize(QSize(300, 38))
    self.main_msg.setAlignment(Qt.AlignCenter)

    # 크롤링 진행상황
    style_sheet = """
      QLabel{
        padding:0px, border:0px
      }
    """
    self.crawled_msg = QLabel("", self)  # 크롤링 완료 된 갯수
    self.crawled_msg.setGeometry(0, 0, 100, 38)
    self.crawled_msg.setAlignment(Qt.AlignCenter | Qt.AlignBottom)
    self.crawled_msg.font().setPointSize(15)
    self.crawled_msg.setStyleSheet(style_sheet)
    self.count_msg = QLabel("", self)  # 확인한 특허정보 갯수
    self.count_msg.setGeometry(100, 0, 100, 38)
    self.count_msg.setAlignment(Qt.AlignRight | Qt.AlignBottom)
    self.count_msg.font().setPointSize(15)
    self.count_msg.setStyleSheet(style_sheet)
    self.limit_msg = QLabel("", self)  # 전체 검색결과 갯수
    self.limit_msg.setGeometry(200, 0, 100, 38)
    self.limit_msg.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
    self.limit_msg.font().setPointSize(15)
    self.limit_msg.setStyleSheet(style_sheet)

    layout = QBoxLayout(QBoxLayout.TopToBottom, parent=self)
    self.setLayout(layout)
    self.progress_bar = QProgressBar()
    self.progress_bar.setGeometry(35, 45, 200, 25)
    self.progress_bar.setStyleSheet("text-align: center;")
    layout.addWidget(self.progress_bar)

    # 크롤러 쓰레드의 신호(signal) 수신
    self.crawl_thread.limit_signal.connect(self.sc.set_limit)
    self.crawl_thread.total_count_signal.connect(self.progress_bar.setValue)
    self.crawl_thread.total_count_signal.connect(self.sc.set_count)
    self.crawl_thread.crawled_count_signal.connect(self.sc.set_crawled)
    self.crawl_thread.result_signal.connect(self.sc.check_result)

    # 크롤러 닫기 버튼
    QToolTip.setFont(QFont('SansSerif', 10))
    self.btn_quit = QPushButton("중지", self)
    self.btn_quit.move(210, 70)
    self.btn_quit.resize(QSize(86, 24))
    self.btn_quit.setDisabled(True)
    self.btn_quit.clicked.connect(self.close_crawler)



app = QApplication(sys.argv)
