import sys

from PyQt5.QtWidgets import (
  QApplication,
  QDialog,
  QTableWidget,
  QPushButton,
  QMessageBox,
  QTableWidgetItem,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from modules.path_gatter import get_img_path

class Scoreboard(QDialog):
  def __init__(self, scoreboard):
    super().__init__()
    self.scoreboard = scoreboard
    self.initUI()
    self.game_trigger = False


  def start_game(self):
    self.game_trigger = True


  def closeEvent(self, event):
    if self.game_trigger:
      self.close()
    else:
      close_box = QMessageBox()
      close = close_box.critical(self, "Close", "종료 하시겠습니까?", QMessageBox.Yes | QMessageBox.No)
      if close == QMessageBox.Yes:
        sys.exit()
      else:
        event.ignore()


  def initUI(self):
    self.setWindowTitle("Dot4 Scoreboard")
    self.resize(300, 500)
    self.setWindowIcon(QIcon(get_img_path("./img/target.png")))
    self.setWindowFlag(Qt.WindowContextHelpButtonHint , False)

    table = QTableWidget(self)
    table.setEditTriggers(QTableWidget.NoEditTriggers)  # 수정 트리거 제거
    table.setGeometry(25,50,250,332)
    table.setColumnCount(3)
    table.setRowCount(11)
    table.verticalHeader().hide()  # row(세로) 번호 숨기기
    table.horizontalHeader().hide()  # column(가로) 번호 숨기기
    table.setColumnWidth(0, 48)  # 0번 컬럼 너비
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
    table.setItem(0,1,QTableWidgetItem("이름"))
    table.setItem(0,2,QTableWidgetItem("평균 시간(초)"))
    table.item(0,1).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
    table.item(0,2).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

    for i in range(len(self.scoreboard)):
      table.setItem(i+1,0,QTableWidgetItem(f'{i+1}위'))
      table.setItem(i+1,1,QTableWidgetItem(self.scoreboard[i]["name"]))
      table.setItem(i+1,2,QTableWidgetItem(f'{self.scoreboard[i]["record"]:.4f}'))
      for j in range(3):
        table.item(i+1,j).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

    start_btn = QPushButton("게임 시작", self)
    start_btn.setGeometry(80,410,140,60)
    start_btn.clicked.connect(self.start_game)
    start_btn.clicked.connect(self.close)





app = QApplication(sys.argv)
