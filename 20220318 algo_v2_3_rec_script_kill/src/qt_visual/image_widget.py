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

import configs


class ImageWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.contentType = "img"
        self.url = None
        self.clubLabel = None
        self.imageLabel = QLabel()
