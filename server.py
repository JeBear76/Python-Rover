# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 18:49:36 2019

@author: jerep_000
"""

from flask import Flask, Response, render_template
import videostream as vs
import os
import robot_controller as rbc
import threading
import time
from werkzeug.serving import make_server

class ServerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.srv = make_server('0.0.0.0', 3000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        print('starting server')
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()
        
app = Flask(__name__)

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    global appCamera
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
    global server
    global appCamera
    global robot
    robot.threadActive = False
    time.sleep(1)
    print('controls shutdown')
    server.shutdown()
    print('server shutdown')

if __name__ == '__main__':
    global server
    global appCamera
    global robot
    appCamera = vs.VideoStream()
    server = ServerThread(app)
    server.start()
    print('server started')
    robot = rbc.Robot_Controller(appCamera)
    robot.StartThisThing()
    print('controls started')
    
