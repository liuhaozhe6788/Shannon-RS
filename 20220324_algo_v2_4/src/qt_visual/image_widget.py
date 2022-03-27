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
from socket import error as SocketError
import errno
from video_widget import VideoWidget


class ImageWidget(VideoWidget):

    def __init__(self, url=None, itemID=None, club=None):
        super().__init__(url, itemID, club)

    def add_img(self):
        image_data = None
        try:
            image_data = requests.get(self.url).content
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise  # Not error we are looking for
            pass  # Handle error here
        return image_data
