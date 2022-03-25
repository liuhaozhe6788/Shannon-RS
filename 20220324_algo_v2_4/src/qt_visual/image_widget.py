# encoding: utf-8
import sys
import os
import requests
from time import sleep
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from socket import error as SocketError
import errno

import configs


class ImageWidget(QWidget):

    def __init__(self, url=None, itemID=None, club=None):
        super().__init__()
        self.contentType = "img"
        self.url = url
        self.itemID = itemID
        self.club = club
        self.imageLabel = QLabel()
        self.clubLabel = QLabel(f"{self.itemID}\n{self.club}")
        self.layout = QVBoxLayout()
        self.height = 300
        self.fontSize = 12

        self.setLayout(self.layout)
        self.layout.addWidget(self.imageLabel)
        self.layout.addWidget(self.clubLabel)

    def add_img(self):
        image = QImage()
        try:
            image_data = requests.get(self.url).content
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise  # Not error we are looking for
            pass  # Handle error here
        image.loadFromData(image_data)
        sleep(1)
        pix_map = QPixmap(image)
        self.imageLabel.setPixmap(pix_map.scaled(int(pix_map.width() / pix_map.height() * self.height), self.height))
        self.imageLabel.setFixedWidth(int(pix_map.width() / pix_map.height() * self.height))

        self.clubLabel.setFont(QFont("Sanserif", self.fontSize))
        self.clubLabel.setFixedWidth(int(pix_map.width() / pix_map.height() * self.height))
        self.setFixedWidth(int(pix_map.width() / pix_map.height() * self.height))

    @property
    def content_type(self):
        return self.contentType

