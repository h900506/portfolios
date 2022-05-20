import sys

from time import time
from random import randint

from PyQt5.QtWidgets import (
  QApplication,
  QMainWindow,
  QPushButton,
  QMessageBox,
  QTableWidget,
  QTableWidgetItem,
  QInputDialog,
  QLabel,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QIcon

from modules.scoreboard import Scoreboard
from modules.control_json import check_json, update_json
from modules.path_gatter import get_img_path

class Dot4(QMainWindow):
  def __init__(self):
    super().__init__()
    self.initUI()


  def set_table(self):
    if self.record_list:
      avg = sum(self.record_list)/len(self.record_list)
      self.point_table.setItem(0,0,QTableWidgetItem(f'{self.cnt} 회차 속도'))
      self.point_table.setItem(0,1,QTableWidgetItem(f'{self.record:.4f}초'))
      self.point_table.setItem(1,1,QTableWidgetItem(f'{avg:.4f}초'))
      if self.cnt == 10:
        self.check_rank(avg)
        self.set_new_game()
    else:
      self.point_table.setItem(0,0,QTableWidgetItem("0 회차 속도")) # 당회차 속도
      self.point_table.setItem(0,1,QTableWidgetItem("0.00초"))
      self.point_table.setItem(1,0,QTableWidgetItem("평균 속도")) # 평균 속도
      self.point_table.setItem(1,1,QTableWidgetItem("0.00초"))


  def set_new_game(self):
    self.target_btn.hide()
    self.startTime = 0.0
    self.record = 0.0
    self.record_list = []
    self.cnt = 0
    self.scoreboard = check_json()
    self.board = Scoreboard(self.scoreboard)
    self.board.setWindowModality(Qt.ApplicationModal)
    self.board.show()
    self.board.exec_()
    self.set_table()


  def closeEvent(self, event):
    close_box = QMessageBox()
    close = close_box.question(self, "Close", "종료 하시겠습니까?", QMessageBox.Yes | QMessageBox.No)
    if close == QMessageBox.Yes:
      sys.exit()
    else:
      event.ignore()


  def check_rank(self, avg):
    idx = 0
    while idx<len(self.scoreboard) and idx<10:
      rec = self.scoreboard[idx]
      if avg < rec["record"]:
        break
      idx += 1
    if idx < 10:
      name_input = QInputDialog()
      name_input.setWindowFlag(Qt.WindowCloseButtonHint, False)
      name_input.setWindowFlag(Qt.WindowContextHelpButtonHint , False)
      user_name = name_input.getText(self,"Enter name",f'{idx+1}위 입니다. 이름을 입력 해주세요.')[0]
      if not user_name:
        user_name = "AAA"
      self.scoreboard.insert(idx,{"name":user_name, "record":avg})
      update_json(self.scoreboard)


  def hideButton(self):
    if self.cnt > len(self.record_list):
      self.record = time() - self.startTime
      self.record_list.append(self.record)
      self.target_btn.hide()
      self.set_table()


  def showButton(self):
    self.startTime = time()
    self.target_btn.move(randint(100,960), randint(70,570))
    self.target_btn.show()
    self.target_btn.clicked.connect(self.hideButton)


  def keyPressEvent(self, e) -> None:
    if e.key() == 16777268:  # F5 key
      self.set_new_game()
    if e.key() == 65 and self.target_btn.isHidden():  # a key
      self.cnt += 1
      self.showButton()


  def paintEvent(self, e):
    painter = QPainter()
    painter.begin(self)
    painter.setBrush(Qt.white)
    painter.setPen(QPen(Qt.gray, 3))
    painter.drawRect(100,70,1000,650)
    painter.end()


  def initUI(self):
    self.setWindowTitle("Dot4")
    self.setFixedSize(1200, 800)
    self.setWindowIcon(QIcon(get_img_path("./img/target.png")))

    self.target_btn = QPushButton(self)
    self.target_btn.resize(40,80)

    self.point_table = QTableWidget(self)
    self.point_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 수정 트리거 제거
    self.point_table.setFocusPolicy(Qt.NoFocus)  # 포커스 제거
    self.point_table.setGeometry(997,0,202,62)
    self.point_table.setRowCount(2)  # 세로 길이 지정
    self.point_table.setColumnCount(2)  # 가로 길이 지정
    self.point_table.verticalHeader().hide()  # row(세로) 번호 숨기기
    self.point_table.horizontalHeader().hide()  # column(가로) 번호 숨기기
    self.point_table.setStyleSheet("""
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

    reset_label = QLabel("F5 : 게임 재시작",self)
    reset_label.move(30,20)

    self.show()
    self.set_new_game()



if __name__ == "__main__":
  app = QApplication(sys.argv)
  ex = Dot4()
  sys.exit(app.exec_())
