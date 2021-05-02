from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from ui_poster import Ui_Form

class MainWin(QWidget):
  def __init__(self):
    super().__init__()
    ui = Ui_Form()
    ui.setupUi(self)
    tree = QStandardItemModel()
    item = QStandardItem('text')
    item2 = QStandardItem('text2')
    item.setChild(1, item2)
    tree.setItem(0, item)
    ui.treeView.setModel(tree)

    header = QStandardItemModel(1, 3)
    header.setHorizontalHeaderItem(0, QStandardItem('key'))
    header.setHorizontalHeaderItem(1, QStandardItem('value'))
    header.setHorizontalHeaderItem(2, QStandardItem('description'))
    ui.header_tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    ui.header_tableView.setModel(header)



if __name__ == '__main__':
  app = QApplication()
  main_win = MainWin()
  main_win.show()
  app.exec_()