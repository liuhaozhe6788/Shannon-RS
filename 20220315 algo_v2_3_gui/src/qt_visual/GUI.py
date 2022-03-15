# encoding: utf-8
import sys
import requests
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *


class UI(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("btn.ui", self)  # 导入.ui文件

        self.setFixedWidth(1040)
        self.setFixedHeight(1600)

        # 找到对象
        self.yes_btn = self.findChild(QPushButton, "yes_btn")
        self.line_edit = self.findChild(QLineEdit, "lineEdit")

        self.uid_label = self.findChild(QLabel, "uid_input")
        self.uid_label.setText(f"用户ID")

        self.uid_result = self.findChild(QLabel, "uid_result")
        self.uid_result.setText(f"用户ID: ")

        self.like_prompt = self.findChild(QLabel, "like_prompt")
        self.like_prompt.setText(f"点赞动态: ")

        self.generalized_cf_prompt = self.findChild(QLabel, "generalized_cf_prompt")
        self.generalized_cf_prompt.setText(f"广义协同过滤推荐结果: ")

        self.item_cf_prompt = self.findChild(QLabel, "item_cf_prompt")
        self.item_cf_prompt.setText(f"基于物品的协同过滤推荐结果: ")

        self.like_slider = self.findChild(QSlider, "like_slider")
        self.generalized_cf_slider = self.findChild(QSlider, "generalized_cf_slider")
        self.item_cf_slider = self.findChild(QSlider, "item_cf_slider")

        self.like_layout = self.findChild(QHBoxLayout, "like_layout")
        self.like_image_labels = []

        self.darkMode_btn = self.findChild(QPushButton, "darkMode_btn")
        self.darkMode_btn.setStyleSheet("QPushButton {background-color: black; color: white;}")
        self.dark_flag = 0

        self.yes_btn.clicked.connect(self.yes_btn_signal)
        self.darkMode_btn.clicked.connect(self.darkMode_btn_signal)


    def yes_btn_signal(self):
        uid = self.line_edit.text()
        self.uid_result.setText(f"用户ID: {uid}")
        self.add_image_to_like()


    def darkMode_btn_signal(self):
        if not self.dark_flag:
            self.darkMode_btn.setText("Light Mode")
            self.setStyleSheet("background-color: black")
            self.darkMode_btn.setStyleSheet("QPushButton {background-color: white; color: black;}")
            self.line_edit.setStyleSheet("background-color: white")
            self.uid_label.setStyleSheet("color: white")
            self.uid_result.setStyleSheet("color: white")
            self.like_prompt.setStyleSheet("color: white")
            self.generalized_cf_prompt.setStyleSheet("color: white")
            self.item_cf_prompt.setStyleSheet("color: white")
            self.dark_flag = 1
        else:
            self.darkMode_btn.setText("Dark Mode")
            self.setStyleSheet("background-color: white")
            self.darkMode_btn.setStyleSheet("QPushButton {background-color: black; color: white;}")
            self.uid_label.setStyleSheet("color: black")
            self.uid_result.setStyleSheet("color: black")
            self.like_prompt.setStyleSheet("color: black")
            self.generalized_cf_prompt.setStyleSheet("color: black")
            self.item_cf_prompt.setStyleSheet("color: black")
            self.dark_flag = 0

    def changed_like_slider(self):
        value = self.slider.value()

    def add_image_to_like(self):
        url_image = "https://pictrue01-1304083978.file.myqcloud.com/50692_16408555220965030@%7C%7C@715.000000@%7C%7C@734.000000.png"
        image = QImage()
        image.loadFromData(requests.get(url_image).content)

        self.like_image_labels.append(QLabel(self))
        self.like_image_labels[-1].setPixmap(QPixmap(image))

        self.like_layout.addWidget(self.like_image_labels[-1])



app = QApplication(sys.argv)
window = UI()
window.show()
app.exec_()