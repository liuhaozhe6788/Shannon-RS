# encoding: utf-8
import sys
import os
import requests
import urllib.request
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from icecream import ic

import image_widget
import configs


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

        self.like_image_labels = []  # 动态的图片标签列表，没有则置为“*”
        self.like_club_labels = []  # 动态的CLUB标签列表。每个动态都有CLUB标签
        self.like_Widgets = []  # 呈现动态内容的Widget列表
        self.like_layouts = []  # 呈现动态内容的layout列表
        self.like_videoWidgets = []  # 动态的视频Widget列表，没有则置为“*”
        self.like_media_players = []  # 动态视频的媒体播放器列表，没有则置为“*”
        self.like_video_ctl_layouts = []  # 动态视频的控制组件layout列表，没有则置为“*”
        self.like_play_btns = []  # 动态视频的播放按钮列表，没有则置为“*”
        self.like_sliders = []  # 动态视频的进度条列表，没有则置为“*”

        self.algo_1_image_labels = []  # 动态的图片标签列表，没有则置为“*”
        self.algo_1_club_labels = []  # 动态的CLUB标签列表。每个动态都有CLUB标签
        self.algo_1_Widgets = []  # 呈现动态内容的Widget列表
        self.algo_1_layouts = []  # 呈现动态内容的layout列表
        self.algo_1_videoWidgets = []  # 动态的视频Widget列表，没有则置为“*”
        self.algo_1_media_players = []  # 动态视频的媒体播放器列表，没有则置为“*”
        self.algo_1_video_ctl_layouts = []  # 动态视频的控制组件layout列表，没有则置为“*”
        self.algo_1_play_btns = []  # 动态视频的播放按钮列表，没有则置为“*”
        self.algo_1_sliders = []  # 动态视频的进度条列表，没有则置为“*”

        self.yes_btn.clicked.connect(self.yes_btn_signal)

    def yes_btn_signal(self):
        uid = self.line_edit.text()
        self.uid_result.setText(f"用户ID: {uid}")
        self.delete_all_res()
        self.add_contents(
            "img",
            "https://pictrue01-1304083978.file.myqcloud.com/50692_16408555220965030@%7C%7C@715.000000@%7C%7C@734.000000.png",
            "动态1",
            self.like_image_labels,
            self.like_club_labels,
            self.like_layouts,
            self.like_Widgets,
            self.like_videoWidgets,
            self.like_media_players,
            self.like_video_ctl_layouts,
            self.like_play_btns,
            self.like_sliders,
            self.scrollLikeLayout
        )
        self.add_contents(
            "img",
            "https://pictrue01-1304083978.cos.ap-guangzhou.myqcloud.com/6C05234C6E061CF26411CE949B185139",
            "动态2",
            self.algo_1_image_labels,
            self.algo_1_club_labels,
            self.algo_1_layouts,
            self.algo_1_Widgets,
            self.algo_1_videoWidgets,
            self.algo_1_media_players,
            self.algo_1_video_ctl_layouts,
            self.algo_1_play_btns,
            self.algo_1_sliders,
            self.scrollAlgo_1Layout
        )
        self.add_contents(
            "img",
            "https://pictrue01-1304083978.cos.ap-guangzhou.myqcloud.com/6C05234C6E061CF26411CE949B185139",
            "动态2",
            self.algo_1_image_labels,
            self.algo_1_club_labels,
            self.algo_1_layouts,
            self.algo_1_Widgets,
            self.algo_1_videoWidgets,
            self.algo_1_media_players,
            self.algo_1_video_ctl_layouts,
            self.algo_1_play_btns,
            self.algo_1_sliders,
            self.scrollAlgo_1Layout
        )

    def add_contents(self, content_type_, url_, label_, image_labels_, club_labels_, layouts_, widgets_, video_widgets_, media_players_, video_ctl_layouts_, play_btns_, sliders_, scroll_layout_):
        fixed_height = 400
        font_size = 20
        if content_type_ == "img":
            image = QImage()
            image.loadFromData(requests.get(url_).content)

            pix_map = QPixmap(image)
            image_labels_.append(QLabel())
            image_labels_[-1].setPixmap(pix_map.scaled(int(pix_map.width()/pix_map.height()*fixed_height), fixed_height))
            image_labels_[-1].setFixedWidth(int(pix_map.width()/pix_map.height()*fixed_height))

            video_widgets_.append('*')
            media_players_.append('*')
            video_ctl_layouts_.append('*')
            play_btns_.append('*')
            sliders_.append('*')
            club_labels_.append(QLabel(label_))
            club_labels_[-1].setFont(QFont("Sanserif", font_size))
            club_labels_[-1].setFixedWidth(int(pix_map.width() / pix_map.height() * fixed_height))

            widgets_.append(QWidget())
            layouts_.append(QVBoxLayout())

            widgets_[-1].setLayout(layouts_[-1])
            layouts_[-1].addWidget(image_labels_[-1])
            layouts_[-1].addWidget(club_labels_[-1])
            widgets_[-1].setFixedWidth(int(pix_map.width() / pix_map.height() * fixed_height))
            scroll_layout_.addWidget(widgets_[-1])

        elif content_type_ == "vid":
            urllib.request.urlretrieve(url_, os.path.join(configs.qt_vid_folder_path, "buffer.mp4"))
            image_labels_.append("*")
            media_players_.append(QMediaPlayer(None, QMediaPlayer.VideoSurface))
            video_widgets_.append(QVideoWidget())

            play_btns_.append(QPushButton(""))
            play_btns_[-1].setEnabled(True)
            play_btns_[-1].setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            play_btns_[-1].clicked.connect(lambda: self.play_video(media_players_[-1], play_btns_[-1], os.path.join(configs.qt_vid_folder_path, "buffer.mp4")))

            sliders_.append(QSlider(Qt.Horizontal))
            sliders_[-1].setRange(0, 0)
            sliders_[-1].sliderMoved.connect(lambda: self.set_position(media_players_[-1]))

            video_ctl_layouts_.append(QHBoxLayout())
            video_ctl_layouts_[-1].setContentsMargins(0, 0, 0, 0)

            video_ctl_layouts_[-1].addWidget(play_btns_[-1])
            video_ctl_layouts_[-1].addWidget(self.slider)

            layouts_.append(QVBoxLayout())

            widgets_.append(QWidget())
            widgets_[-1].setLayout(layouts_[-1])
            layouts_[-1].addWidget(video_widgets_[-1])
            layouts_[-1].addWidget(video_ctl_layouts_[-1])
            layouts_[-1].addWidget(club_labels_[-1])

            scroll_layout_.addWidget(widgets_[-1])

            media_players_[-1].setVideoOutput(video_widgets_[-1])

            media_players_[-1].positionChanged.connect(lambda: self.position_changed(sliders_[-1]))
            media_players_[-1].durationChanged.connect(lambda: self.duration_changed(sliders_[-1]))

        else:
            return

    def delete_all_res(self):
        for i in reversed(range(self.scrollLikeLayout.count())):
            self.scrollLikeLayout.itemAt(i).widget().setParent(None)

        for i in reversed(range(self.scrollAlgo_1Layout.count())):
            self.scrollAlgo_1Layout.itemAt(i).widget().setParent(None)

        for i in reversed(range(self.scrollAlgo_2Layout.count())):
            self.scrollAlgo_2Layout.itemAt(i).widget().setParent(None)

    def play_video(self, media_player, play_btn, file_path):
        if media_player.state() == QMediaPlayer.PlayingState:
            media_player.pause()
            play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            if media_player.state() == QMediaPlayer.StoppedState:
                self.open_file(media_player, play_btn, file_path)
            media_player.play()
            play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def position_changed(self, slider_, pos):
        slider_.setValue(pos)

    def duration_changed(self, slider_, dur):
        slider_.setRange(0, dur)

    def set_position(self, media_player, pos):
        media_player.setPosition(pos)

    def open_file(self, media_player, play_btn, file_path):
        media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
        play_btn.setEnabled(True)


app = QApplication(sys.argv)
window = UI()
window.show()
app.exec_()
