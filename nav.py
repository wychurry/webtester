from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Nav(QWidget):

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.treeView = QTreeView(self)
        self.treeView.setObjectName(u"treeView")