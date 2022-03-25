import numpy as np
import cv2
import gst

cap = cv2.VideoCapture('/home/liuhaozhe/PycharmProjects/20220324_algo_v2_4/vid/1917.mp4')

while cap.isOpened():
    ret, frame = cap.read()
    cv2.imshow('frame', frame)
    if cv2.waitKey(40) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
