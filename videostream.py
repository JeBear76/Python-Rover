# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 12:13:50 2019

@author: W7040625
"""
import cv2
import datetime

class VideoStream(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        _, image = self.video.read()

        font = cv2.FONT_HERSHEY_SIMPLEX
        text = "Rover - " +  datetime.datetime.now().strftime("%a %d %m %Y %X")
        image = cv2.putText(image, text, (10, 50), font, 0.75, (255, 0, 255), 2, cv2.LINE_AA)
        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def save_image(self):
        success, image = self.video.read()
        if success:
            text = "Greetings from..."
            font = cv2.FONT_HERSHEY_SIMPLEX
            image = cv2.putText(image, text, (10, 50), font, 0.75, (255, 0, 255), 2, cv2.LINE_AA)
            cv2.imwrite('static/images/' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.png', image)

