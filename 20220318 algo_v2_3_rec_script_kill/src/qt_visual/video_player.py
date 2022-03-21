# encoding:utf-8
import sys
import os
import urllib.request
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from icecream import ic


class UI(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("video_player.ui", self)  # 导入.ui文件

        p = self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)

        # 创建媒体播放器对象
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # 创建videoWidget对象
        self.videoWidget = QVideoWidget()

        # 创建播放按钮
        self.playBtn = QPushButton("")
        self.playBtn.setEnabled(True)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.clicked.connect(self.play_video)

        # 创建进度条
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        # 创建label
        self.label = QLabel()
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # 创建hbox layout
        self.hboxLayout = QHBoxLayout()
        self.hboxLayout.setContentsMargins(0, 0, 0, 0)

        self.hboxLayout.addWidget(self.playBtn)
        self.hboxLayout.addWidget(self.slider)

        self.vboxLayout = QVBoxLayout()
        self.vboxLayout.addWidget(self.videoWidget)
        self.vboxLayout.addLayout(self.hboxLayout)
        self.vboxLayout.addWidget(self.label)

        self.setLayout(self.vboxLayout)

        self.mediaPlayer.setVideoOutput(self.videoWidget)

        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

        url = "https://trends-video-1304083978.file.myqcloud.com/48633_1631758537931.mp4"
        urllib.request.urlretrieve(url, "buffer.mp4")
        self.file_path = "/home/liuhaozhe/SourceCode/PycharmProjects/grad_design/20220318 algo_v2_3_rec_script_kill/src/qt_visual/buffer.mp4"

        if self.mediaPlayer.state() == QMediaPlayer.StoppedState:
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def open_file(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.file_path)))
        self.playBtn.setEnabled(True)

    def play_video(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            if self.mediaPlayer.state() == QMediaPlayer.StoppedState:
                self.open_file()
            self.mediaPlayer.play()
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def position_changed(self, pos):
        self.slider.setValue(pos)

    def duration_changed(self, dur):
        self.slider.setRange(0, dur)

    def set_position(self, pos):
        self.mediaPlayer.setPosition(pos)



app = QApplication(sys.argv)
window = UI()
window.show()
app.exec_()