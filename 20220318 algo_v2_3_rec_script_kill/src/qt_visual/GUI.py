# encoding: utf-8
import sys
import requests
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from icecream import ic


class UI(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("rec_result.ui", self)  # 导入.ui文件

        self.setFixedWidth(1040)
        self.setFixedHeight(1150)

        self.yes_btn = self.findChild(QPushButton, "yes_btn")
        self.line_edit = self.findChild(QLineEdit, "lineEdit")
        self.uid_label = self.findChild(QLabel, "uid_input")
        self.uid_label.setText(f"用户ID")

        self.scrollWindow = self.findChild(QScrollArea, "scrollArea")
        self.scrollWindowWidget = QWidget()
        self.scrollWindowLayout = QVBoxLayout()

        self.scrollLike = QScrollArea()
        self.scrollLikeWidget = QWidget()
        self.scrollLikeLayout = QHBoxLayout()

        self.scrollAlgo_1 = QScrollArea()
        self.scrollAlgo_1Widget = QWidget()
        self.scrollAlgo_1Layout = QHBoxLayout()

        self.scrollAlgo_2 = QScrollArea()
        self.scrollAlgo_2Widget = QWidget()
        self.scrollAlgo_2Layout = QHBoxLayout()

        self.uid_result = QLabel("用户ID: ")
        self.uid_result.setFont(QFont("Sanserif", 20))
        self.uid_result.setFixedHeight(30)
        self.like_prompt = QLabel("点赞动态: ")
        self.like_prompt.setFont(QFont("Sanserif", 20))
        self.like_prompt.setFixedHeight(30)
        self.generalized_cf_prompt = QLabel("广义协同过滤推荐结果: ")
        self.generalized_cf_prompt.setFont(QFont("Sanserif", 20))
        self.generalized_cf_prompt.setFixedHeight(30)
        self.item_cf_prompt = QLabel("基于物品的协同过滤推荐结果: ")
        self.item_cf_prompt.setFont(QFont("Sanserif", 20))

        scrollArea_height = 500

        self.scrollLikeWidget.setLayout(self.scrollLikeLayout)
        self.scrollLike.setWidgetResizable(True)
        self.scrollLike.setFixedHeight(scrollArea_height)
        self.scrollLike.setWidget(self.scrollLikeWidget)

        self.scrollAlgo_1Widget.setLayout(self.scrollAlgo_1Layout)
        self.scrollAlgo_1.setWidgetResizable(True)
        self.scrollAlgo_1.setFixedHeight(scrollArea_height)
        self.scrollAlgo_1.setWidget(self.scrollAlgo_1Widget)

        self.scrollAlgo_2Widget.setLayout(self.scrollAlgo_2Layout)
        self.scrollAlgo_2.setWidgetResizable(True)
        self.scrollAlgo_2.setFixedHeight(scrollArea_height)
        self.scrollAlgo_2.setWidget(self.scrollAlgo_2Widget)

        self.scrollWindowLayout.addWidget(self.uid_result)
        self.scrollWindowLayout.addWidget(self.like_prompt)
        self.scrollWindowLayout.addWidget(self.scrollLike)
        self.scrollWindowLayout.addWidget(self.generalized_cf_prompt)
        self.scrollWindowLayout.addWidget(self.scrollAlgo_1)
        self.scrollWindowLayout.addWidget(self.item_cf_prompt)
        self.scrollWindowLayout.addWidget(self.scrollAlgo_2)

        self.scrollWindowWidget.setLayout(self.scrollWindowLayout)
        # self.scrollWindow.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollWindow.setWidgetResizable(True)
        self.scrollWindow.setFixedHeight(1050)
        self.scrollWindow.setWidget(self.scrollWindowWidget)

        self.vLayout = self.findChild(QVBoxLayout, "verticalLayout")
        self.vLayout.addWidget(self.scrollWindow)
        self.setLayout(self.vLayout)

        self.like_image_labels = []
        self.like_club_labels = []
        self.like_Widgets = []
        self.like_layouts = []
        self.yes_btn.clicked.connect(self.yes_btn_signal)

    def yes_btn_signal(self):
        uid = self.line_edit.text()
        self.uid_result.setText(f"用户ID: {uid}")
        self.add_image_to_like(
            "https://pictrue01-1304083978.file.myqcloud.com/50692_16408555220965030@%7C%7C@715.000000@%7C%7C@734.000000.png",
            "动态1")
        self.add_image_to_like(
            "https://pictrue01-1304083978.cos.ap-guangzhou.myqcloud.com/6C05234C6E061CF26411CE949B185139",
            "动态2")
        self.add_vid_to_like(
            ""
        )

    def add_image_to_like(self, url_image, label):
        fixed_height = 400
        font_size = 20
        image = QImage()
        image.loadFromData(requests.get(url_image).content)

        pix_map = QPixmap(image)
        self.like_image_labels.append(QLabel())
        self.like_image_labels[-1].setPixmap(pix_map.scaled(int(pix_map.width()/pix_map.height()*fixed_height), fixed_height))
        self.like_image_labels[-1].setFixedWidth(int(pix_map.width()/pix_map.height()*fixed_height))
        self.like_club_labels.append(QLabel(label))
        self.like_club_labels[-1].setFont(QFont("Sanserif", font_size))
        self.like_club_labels[-1].setFixedWidth(int(pix_map.width()/pix_map.height()*fixed_height))
        self.like_Widgets.append(QWidget())
        self.like_layouts.append(QVBoxLayout())

        self.like_Widgets[-1].setLayout(self.like_layouts[-1])
        self.like_layouts[-1].addWidget(self.like_image_labels[-1])
        self.like_layouts[-1].addWidget(self.like_club_labels[-1])
        self.like_Widgets[-1].setFixedWidth(int(pix_map.width()/pix_map.height()*fixed_height))
        self.scrollLikeLayout.addWidget(self.like_Widgets[-1])


app = QApplication(sys.argv)
window = UI()
window.show()
app.exec_()
