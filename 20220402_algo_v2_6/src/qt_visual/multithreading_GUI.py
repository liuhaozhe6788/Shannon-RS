# encoding: utf-8
import sys
sys.dont_write_bytecode = True
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
from algos import GeneralizedCF, ItemCF, UserCF


logging.basicConfig(format="%(message)s", level=logging.INFO)

N = 0


class WorkerSignals(QObject):
    finish = pyqtSignal(bytes)
    finish_all = pyqtSignal(bool)


class Runnable(QRunnable):
    def __init__(self, scroll_widget, n, n_threads):
        self.widget = scroll_widget
        self.n = n
        self.n_threads = n_threads
        self.signals = WorkerSignals()
        super().__init__()

    # GUI界面的更新不能运行在子线程中
    def run(self):
        global N
        frame_data = self.widget.add_img()
        N = N + 1
        logging.info(f"thread No.{self.n} is finished, {N}/{self.n_threads} threads are finished")
        self.signals.finish.emit(frame_data)  # 图片下载完后，发出信号给GUI，用于界面的更新，显示图片

        if N == self.n_threads:
            logging.info(f"all {N} contents downloaded")
            self.signals.finish_all.emit(True)


class UI(QWidget):
    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        uic.loadUi("rec_result.ui", self)  # 导入.ui文件

        utils.create_folder_paths()

        self.db = db
        self.item_cf = ItemCF(self.db)
        self.item_cf.get_top_n()
        self.user_cf = UserCF(self.db)
        self.user_cf.get_top_n()
        self.generalized_cf = None

        self.setFixedWidth(1850)
        self.setFixedHeight(1000)

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

        self.scrollAlgo_3 = QScrollArea()
        self.scrollAlgo_3Widget = QWidget()
        self.scrollAlgo_3Layout = QHBoxLayout()

        self.uid_result = QLabel("用户ID: ")
        self.uid_result.setFont(QFont("Sanserif", 15))
        self.uid_result.setFixedHeight(30)
        self.like_prompt = QLabel("由于您已点赞了如下动态: ")
        self.like_prompt.setFont(QFont("Sanserif", 15))
        self.like_prompt.setFixedHeight(30)
        self.generalized_cf_prompt = QLabel("广义协同过滤给您推荐如下动态: ")
        self.generalized_cf_prompt.setFont(QFont("Sanserif", 15))
        self.generalized_cf_prompt.setFixedHeight(30)
        self.item_cf_prompt = QLabel("基于物品的协同过滤给您推荐如下动态: ")
        self.item_cf_prompt.setFont(QFont("Sanserif", 15))
        self.item_cf_prompt.setFixedHeight(30)
        self.user_cf_prompt = QLabel("基于用户的协同过滤给您推荐如下动态: ")
        self.user_cf_prompt.setFont(QFont("Sanserif", 15))
        self.user_cf_prompt.setFixedHeight(30)

        scrollArea_height = 650

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

        self.scrollAlgo_3Widget.setLayout(self.scrollAlgo_3Layout)
        self.scrollAlgo_3.setWidgetResizable(True)
        self.scrollAlgo_3.setFixedHeight(scrollArea_height)
        self.scrollAlgo_3.setWidget(self.scrollAlgo_3Widget)

        self.scrollWindowLayout.addWidget(self.uid_result)
        self.scrollWindowLayout.addWidget(self.like_prompt)
        self.scrollWindowLayout.addWidget(self.scrollLike)
        self.scrollWindowLayout.addWidget(self.generalized_cf_prompt)
        self.scrollWindowLayout.addWidget(self.scrollAlgo_1)
        self.scrollWindowLayout.addWidget(self.item_cf_prompt)
        self.scrollWindowLayout.addWidget(self.scrollAlgo_2)
        self.scrollWindowLayout.addWidget(self.user_cf_prompt)
        self.scrollWindowLayout.addWidget(self.scrollAlgo_3)

        self.scrollWindowWidget.setLayout(self.scrollWindowLayout)
        # self.scrollWindow.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollWindow.setWidgetResizable(True)
        # self.scrollWindow.setFixedHeight(1050)
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
        self.yes_btn.setEnabled(False)
        global N
        N = 0
        uid = self.line_edit.text()
        self.uid_result.setText(f"用户ID: {uid}")
        self.delete_all_res()
        self.scrollWidgets = []
        like_items = self.db.get_objs(['user', uid, 'like', 'item'], key="动态")
        like_items.reverse()
        # n_items_max = 30
        # like_items = like_items[: min(n_items_max, len(like_items))]

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
                    self.scrollLikeLayout
                )

        self.generalized_cf = GeneralizedCF(uid, self.db)
        algo_1_items = self.generalized_cf.run_generalized_cf()
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
                    self.scrollAlgo_1Layout
                )

        algo_2_items = self.item_cf.run(uid)
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
                    self.scrollAlgo_2Layout
                )

        algo_3_items = self.user_cf.run(uid)
        for algo_3_item in algo_3_items:
            algo_3_item_club = ",".join((list(filter(lambda x: ":".join(x.split(":")[-2:]), self.db.get_objs(['item', algo_3_item, 'have', 'club'], key="动态")))))
            if algo_3_item_url := self.db.get_objs(['item', algo_3_item, 'have', 'image_url']):
                self.add_widgets(
                    "img",
                    algo_3_item_url[0],
                    algo_3_item.split(":")[-1],
                    ":".join(algo_3_item_club.split(":")[-2:]),
                    self.scrollAlgo_3Layout
                )
            elif algo_3_item_url := self.db.get_objs(['item', algo_3_item, 'have', 'video_url']):
                self.add_widgets(
                    "vid",
                    algo_3_item_url,
                    algo_3_item.split(":")[-1],
                    ":".join(algo_3_item_club.split(":")[-2:]),
                    self.scrollAlgo_3Layout
                )

        # # 用于调试
        # for i in range(300):
        #     self.add_widgets(
        #         "vid",
        #         "https://trends-video-1304083978.file.myqcloud.com/48622_1630374360300.mp4",
        #         "动态2",
        #         "追星",
        #         self.scrollLikeLayout,
        #     )
        #     self.add_widgets(
        #         "img",
        #         "https://pictrue01-1304083978.file.myqcloud.com/48660_16282286980466098_828.000000*992.000000.png",
        #         "动态2",
        #         "追星",
        #         self.scrollLikeLayout,
        #     )


        self.add_contents()

    def add_widgets(self, content_type_, url_, itemid_, club_, scroll_layout_):
        if content_type_ == "img":
            img_widget = image_widget.ImageWidget(url_, itemid_, club_)
            scroll_layout_.addWidget(img_widget)
            self.scrollWidgets.append(img_widget)

        elif content_type_ == "vid":
            vid_widget = video_widget.VideoWidget(url_, itemid_, club_)
            scroll_layout_.addWidget(vid_widget)
            self.scrollWidgets.append(vid_widget)
        else:
            return

    def add_contents(self):
        pool = QThreadPool.globalInstance()
        logging.info(f"Running {len(self.scrollWidgets)} Threads")
        for i in range(len(self.scrollWidgets)):
            runnable = Runnable(self.scrollWidgets[i], i, len(self.scrollWidgets))
            runnable.signals.finish.connect(self.scrollWidgets[i].updateUI)
            runnable.signals.finish_all.connect(lambda x: self.yes_btn.setEnabled(x))
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