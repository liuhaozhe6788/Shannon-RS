# encoding: utf-8
import sys
sys.dont_write_bytecode = True
import os
import requests
from time import sleep
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from video_widget import VideoWidget


class ImageWidget(VideoWidget):

    def __init__(self, url=None, itemID=None, club=None):
        super().__init__(url, itemID, club)

    def add_img(self):
        image_data = requests.get(self.url).content
        return image_data
