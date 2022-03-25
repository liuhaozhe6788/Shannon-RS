# encoding: utf-8
import sys
import os
import logging
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import image_widget
import video_widget
import configs
import database
import utils
from algo_list import run_all_algos

logging.basicConfig(format="%(message)s", level=logging.INFO)

N = 0


class Runnable(QRunnable):
    def __init__(self, scroll_widget, n, n_threads):
        self.widget = scroll_widget
        self.n = n
        self.n_threads = n_threads
        super().__init__()

    def run(self):
        global N
        if self.widget.content_type == "img":
            self.widget.add_img()
            N = N + 1
            logging.info(f"Thread {self.n} is finished, {N} threads are finished")

        elif self.widget.content_type == "vid":
            self.widget.add_vid()
            N = N + 1
            logging.info(f"Thread {self.n} is finished, {N} threads are finished")

        else:
            return

        if N == self.n_threads:
            logging.info(f"all {N} contents downloaded")
            N == 0


class UI(QWidget):
    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        uic.loadUi("rec_result.ui", self)  # 导入.ui文件

        utils.create_folder_paths()

        self.db = db
        self.rec_res = run_all_algos(self.db)

        self.setFixedWidth(1850)
        self.setFixedHeight(1150)

        # 增加用户ID输入框
        self.yes_btn = QPushButton()
        self.yes_btn.setFixedHeight(30)
        self.yes_btn.setIcon(QIcon(os.path.join(configs.qt_img_folder_path, "yes.jpeg")))
        self.yes_btn.setIconSize(QSize(30, 30))
        self.line_edit = QLineEdit()
        self.line_edit.setFixedHeight(30)
        self.uid_label = QLabel("用户ID:")
        self.uid_label.setFont(QFont("Sanserif", 20))
        self.uid_label.setFixedHeight(30)

        self.inputWidget = QWidget()
        self.inputLayout = QHBoxLayout()

        self.scrollWindow = QScrollArea()
        self.scrollWindowWidget = QWidget()
        self.scrollWindowLayout = QVBoxLayout()

        self.scrollLike = QScrollArea()  # 滚动区域
        self.scrollLikeWidget = QWidget()  # 滚动区域内的Widget
        self.scrollLikeLayout = QHBoxLayout()  # 滚动区域内Widget的layout

        self.scrollAlgo_1 = QScrollArea()
        self.scrollAlgo_1Widget = QWidget()
        self.scrollAlgo_1Layout = QHBoxLayout()

        self.scrollAlgo_2 = QScrollArea()
        self.scrollAlgo_2Widget = QWidget()
        self.scrollAlgo_2Layout = QHBoxLayout()

        self.uid_result = QLabel("用户ID: ")
        self.uid_result.setFont(QFont("Sanserif", 20))
        self.uid_result.setFixedHeight(30)
        self.like_prompt = QLabel("由于您已点赞了如下动态: ")
        self.like_prompt.setFont(QFont("Sanserif", 20))
        self.like_prompt.setFixedHeight(30)
        self.generalized_cf_prompt = QLabel("广义协同过滤给您推荐如下动态: ")
        self.generalized_cf_prompt.setFont(QFont("Sanserif", 20))
        self.generalized_cf_prompt.setFixedHeight(30)
        self.item_cf_prompt = QLabel("基于物品的协同过滤给您推荐如下动态: ")
        self.item_cf_prompt.setFont(QFont("Sanserif", 20))

        scrollArea_height = 400

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

        self.inputWidget.setLayout(self.inputLayout)
        self.inputLayout.addWidget(self.uid_label)
        self.inputLayout.addWidget(self.line_edit)
        self.inputLayout.addWidget(self.yes_btn)

        self.vLayout = QVBoxLayout()
        self.vLayout.addWidget(self.inputWidget)
        self.vLayout.addWidget(self.scrollWindow)
        self.setLayout(self.vLayout)

        self.scrollWidgets = []

        self.yes_btn.clicked.connect(self.yes_btn_signal)

    def yes_btn_signal(self):
        print("yes button clicked")
        uid = self.line_edit.text()
        self.uid_result.setText(f"用户ID: {uid}")
        self.delete_all_res()
        self.scrollWidgets = []
        like_items = self.db.get_objs(['user', uid, 'like', 'item'], key="动态")
        like_items.reverse()
        n_items_max = 30
        like_items = like_items[: min(n_items_max, len(like_items))]

        for like_item in like_items:
            like_item_club = ",".join((list(filter(lambda x: ":".join(x.split(":")[-2:]), self.db.get_objs(['item', like_item, 'have', 'club'], key="动态")))))
            if like_item_url := self.db.get_objs(['item', like_item, 'have', 'image_url']):
                self.add_widgets(
                    "img",
                    like_item_url[0],
                    like_item.split(":")[-1],
                    ":".join(like_item_club.split(":")[-2:]),
                    self.scrollLikeLayout
                )
            elif like_item_url := self.db.get_objs(['item', like_item, 'have', 'video_url']):
                self.add_widgets(
                    "vid",
                    like_item_url,
                    like_item.split(":")[-1],
                    ":".join(like_item_club.split(":")[-2:]),
                    self.scrollLikeLayout,
                    like_item.split(":")[-1]
                )
        algo_1_res, algo_2_res = self.rec_res

        algo_1_items = list(algo_1_res.loc[algo_1_res["user"] == uid, "recommendation"])[0]
        n_items_max = 20
        algo_1_items = algo_1_items[: min(n_items_max, len(algo_1_items))]

        for algo_1_item in algo_1_items:
            algo_1_item_club = ",".join((list(filter(lambda x: ":".join(x.split(":")[-2:]), self.db.get_objs(['item', algo_1_item, 'have', 'club'], key="动态")))))
            if algo_1_item_url := self.db.get_objs(['item', algo_1_item, 'have', 'image_url']):
                self.add_widgets(
                    "img",
                    algo_1_item_url[0],
                    algo_1_item.split(":")[-1],
                    ":".join(algo_1_item_club.split(":")[-2:]),
                    self.scrollAlgo_1Layout
                )
            elif algo_1_item_url := self.db.get_objs(['item', algo_1_item, 'have', 'video_url']):
                self.add_widgets(
                    "vid",
                    algo_1_item_url,
                    algo_1_item.split(":")[-1],
                    ":".join(algo_1_item_club.split(":")[-2:]),
                    self.scrollAlgo_1Layout,
                    algo_1_item.split(":")[-1]
                )

        algo_2_items = list(algo_2_res.loc[algo_2_res["user"] == uid, "recommendation"])[0]
        n_items_max = 20
        algo_2_items = algo_2_items[: min(n_items_max, len(algo_2_items))]

        for algo_2_item in algo_2_items:
            algo_2_item_club = ",".join((list(filter(lambda x: ":".join(x.split(":")[-2:]), self.db.get_objs(['item', algo_2_item, 'have', 'club'], key="动态")))))
            if algo_2_item_url := self.db.get_objs(['item', algo_2_item, 'have', 'image_url']):
                self.add_widgets(
                    "img",
                    algo_2_item_url[0],
                    algo_2_item.split(":")[-1],
                    ":".join(algo_2_item_club.split(":")[-2:]),
                    self.scrollAlgo_2Layout
                )
            elif algo_2_item_url := self.db.get_objs(['item', algo_2_item, 'have', 'video_url']):
                self.add_widgets(
                    "vid",
                    algo_2_item_url,
                    algo_2_item.split(":")[-1],
                    ":".join(algo_2_item_club.split(":")[-2:]),
                    self.scrollAlgo_2Layout,
                    algo_2_item.split(":")[-1]
                )

        # for i in range(3):
        #     self.add_widgets(
        #         "vid",
        #         "https://trends-video-1304083978.file.myqcloud.com/48622_1630374360300.mp4",
        #         "动态2",
        #         "追星",
        #         self.scrollLikeLayout,
        #         "动态2"
        #     )

        self.add_contents()

    def add_widgets(self, content_type_, url_, itemid_, club_, scroll_layout_, buffer_name_=None):
        if content_type_ == "img":
            img_widget = image_widget.ImageWidget(url_, itemid_, club_)
            scroll_layout_.addWidget(img_widget)
            self.scrollWidgets.append(img_widget)

        elif content_type_ == "vid":
            vid_widget = video_widget.VideoWidget(url_, itemid_, club_, buffer_name_)
            scroll_layout_.addWidget(vid_widget)
            self.scrollWidgets.append(vid_widget)
        else:
            return

    def add_contents(self):
        pool = QThreadPool.globalInstance()
        logging.info(f"Running {len(self.scrollWidgets)} Threads")
        for i in range(len(self.scrollWidgets)):
            runnable = Runnable(self.scrollWidgets[i], i, len(self.scrollWidgets))
            pool.start(runnable)

    def delete_all_res(self):
        for i in reversed(range(self.scrollLikeLayout.count())):
            self.scrollLikeLayout.itemAt(i).widget().setParent(None)

        for i in reversed(range(self.scrollAlgo_1Layout.count())):
            self.scrollAlgo_1Layout.itemAt(i).widget().setParent(None)

        for i in reversed(range(self.scrollAlgo_2Layout.count())):
            self.scrollAlgo_2Layout.itemAt(i).widget().setParent(None)


app = QApplication(sys.argv)
window = UI(database.DataBase(os.path.join(configs.data_folder_path, "data_20220222.xlsx")))
window.show()
app.exec_()
