import sys
import requests
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import Qt


class UI(QWidget):
    def __init__(self, val):
        super().__init__()

        self.scroll = QScrollArea()
        self.formLayout = QFormLayout()
        self.groupBox = QGroupBox("This is a group box")

        self.labelList = []
        self.buttonList = []

        for i in range(val):
            self.labelList.append(QLabel(f"{i}"))
            self.buttonList.append(QPushButton(f"{i}"))
            self.formLayout.addRow(self.labelList[i], self.buttonList[i])

        self.groupBox.setLayout(self.formLayout)
        self.scroll.setWidget(self.groupBox)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(400)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.scroll)

        self.setLayout(self.layout)


app = QApplication(sys.argv)
window = UI(40)
window.show()
app.exec_()