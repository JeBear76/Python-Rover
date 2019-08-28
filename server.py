# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 18:49:36 2019

@author: jerep_000
"""

from flask import Flask, Response, render_template
app = Flask(__name__)
import videostream as vs
import os
import robot_controller as rbc
import time
from sys import exit

appCamera = None
robot = None

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(appCamera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/gallery')
def static_images():
    try:
        lst = os.listdir('static/')
    except OSError:
        pass

    return render_template('gallery.html', files = lst)

@app.route('/shutdown')
def shutdown():
    robot.threadActive = False
    time.sleep(1)
    exit(0)

if __name__ == '__main__':
    appCamera = vs.VideoStream()
    robot = rbc.Robot_Controller(appCamera)
    robot.StartThisThing()
    app.run(host='0.0.0.0', port=3000)
