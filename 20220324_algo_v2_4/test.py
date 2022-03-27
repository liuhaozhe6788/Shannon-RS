import os
import urllib.request
import sys
sys.dont_write_bytecode = True
import cv2
import requests

import configs
import utils


utils.create_folder_paths()
url = "https://trends-video-1304083978.file.myqcloud.com/48633_1631756953827.mp4"

file_path = os.path.join(configs.qt_vid_folder_path, f"buffer.mp4")
cap = cv2.VideoCapture(url)
fps = cap. get(cv2. CAP_PROP_FPS)
cap.set(cv2.CAP_PROP_POS_MSEC, fps/20)

ret, frame = cap.read()
# print(type(frame))

if ret:
    cv2.imwrite("frame20sec.jpg", frame)     # save frame as JPEG file

url = "https://pictrue01-1304083978.file.myqcloud.com/48660_16282286980466098_828.000000*992.000000.png"
image_data = requests.get(url).content
print(type(image_data))

