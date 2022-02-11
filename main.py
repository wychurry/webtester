from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from nav import Nav

class MainWin(QWidget):
  def __init__(self):
    super().__init__()
    self.setMinimumSize(QSize(800, 600))
    
    # self.splitter = QSplitter(self)
    # self.splitter.setObjectName(u"splitter")
    # self.splitter.setOrientation(Qt.Horizontal)
    # self.splitter.setHandleWidth(10)
    # self.splitter.setChildrenCollapsible(False)


    # self.nav = Nav(self.splitter)
    # self.btn = QPushButton(self.splitter)
    # self.btn2 = QPushButton(self.splitter)

    # sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    # sizePolicy.setHorizontalStretch(0)
    # sizePolicy.setVerticalStretch(0)
    # sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
    # self.setSizePolicy(sizePolicy)
    # self.setSizeIncrement(QSize(100, 0))
    # self.setBaseSize(QSize(10, 20))
    # self.setLayoutDirection(Qt.LeftToRight)

    self.verticalLayout = QVBoxLayout(self)
    self.verticalLayout.setObjectName(u"verticalLayout")
    self.verticalLayout.addChildWidget(QPushButton("1"))
    self.verticalLayout.addChildWidget(QPushButton("12"))
    self.verticalLayout.setContentsMargins(QMargins(0,0,0,0))
    self.setContentsMargins(QMargins(0,0,0,0))
    # self.verticalLayout.addChildWidget(self.splitter)



if __name__ == '__main__':
  app = QApplication()
  main_win = MainWin()
  main_win.show()
  app.exec_()