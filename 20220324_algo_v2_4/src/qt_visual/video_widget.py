# encoding: utf-8
import sys
import os
import requests
from time import sleep
import urllib.request
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2
from socket import error as SocketError
import errno

import configs


class VideoWidget(QWidget):

    def __init__(self, url=None, itemID=None, club=None, buffer_name=None):
        super().__init__()
        self.contentType = "vid"
        self.url = url
        self.itemID = itemID
        self.club = club
        self.clubLabel = QLabel(f"{self.itemID}\n{self.club}")
        self.bufferName = buffer_name
        self.layout = QVBoxLayout()
        self.height = 300
        self.fontSize = 12

        self.clubLabel.setFont(QFont("Sanserif", self.fontSize))

        # 创建媒体播放器对象
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # 创建videoWidget对象
        self.videoWidget = QVideoWidget()

        # 创建播放按钮
        self.playBtn = QPushButton("")
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.clicked.connect(self.play_video)

        # 创建进度条
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        # 创建hbox layout
        self.videoCtrlLayout = QHBoxLayout()
        self.videoCtrlLayout.setContentsMargins(0, 0, 0, 0)

        self.videoCtrlLayout.addWidget(self.playBtn)
        self.videoCtrlLayout.addWidget(self.slider)

        self.videoCtrlWidget = QWidget()
        self.videoCtrlWidget.setLayout(self.videoCtrlLayout)

        self.setLayout(self.layout)
        self.layout.addWidget(self.videoWidget)
        self.layout.addWidget(self.videoCtrlWidget)
        self.layout.addWidget(self.clubLabel)

        self.mediaPlayer.setVideoOutput(self.videoWidget)

    def add_vid(self):
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

        self.file_path = os.path.join(configs.qt_vid_folder_path, f"{self.bufferName}.mp4")

        try:
            urllib.request.urlretrieve(self.url, self.file_path)
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise  # Not error we are looking for
            pass  # Handle error here

        sleep(1)
        vid = cv2.VideoCapture(self.file_path)
        self.vidHeight = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.vidWdith = vid.get(cv2.CAP_PROP_FRAME_WIDTH)

        self.videoWidget.setFixedWidth(int(self.vidWdith / self.vidHeight * self.height))
        self.videoCtrlWidget.setFixedWidth(int(self.vidWdith / self.vidHeight * self.height))
        self.clubLabel.setFixedWidth(int(self.vidWdith / self.vidHeight * self.height))
        self.setFixedWidth(int(self.vidWdith / self.vidHeight * self.height))

        self.open_file()

    def open_file(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.file_path)))
        self.playBtn.setEnabled(True)
        # self.mediaPlayer.play()
        # self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def play_video(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            # if self.mediaPlayer.state() == QMediaPlayer.StoppedState:
            #     self.open_file()
            self.mediaPlayer.play()
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def position_changed(self, pos):
        self.slider.setValue(pos)

    def duration_changed(self, dur):
        self.slider.setRange(0, dur)

    def set_position(self, pos):
        self.mediaPlayer.setPosition(pos)

    @property
    def content_type(self):
        return self.contentType
