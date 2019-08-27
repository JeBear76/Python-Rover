# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 12:13:50 2019

@author: W7040625
"""
import cv2
import datetime

class VideoStream(object):
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video = cv2.VideoCapture(0)
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')

    def __del__(self):
        self.video.release()

    def get_frame(self):
        _, image = self.video.read()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.

        font = cv2.FONT_HERSHEY_SIMPLEX
        text = "Rover - " +  datetime.datetime.now().strftime("%a %d %m %Y %X")
        image = cv2.putText(image, text, (10, 50), font, 0.75, (255, 0, 255), 2, cv2.LINE_AA)

        ret, jpeg = cv2.imencode('.png', image)
        return jpeg.tobytes()