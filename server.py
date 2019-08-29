# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 18:49:36 2019

@author: jerep_000
"""

from flask import Flask, Response, render_template, request
from flask_socketio import SocketIO
import json

import os
import socket
import logging

import videostream as vs
import threading

import robot_controller as rbc

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

server_port = 3000
video_port = 3001   
app = Flask(__name__)
videoapp = Flask('videoApp')
app.config['SECRET_KEY'] = 'secretKey'
socketio = SocketIO(app)

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@socketio.on('event')
def handle_event(message):
    logging.info(message)

@socketio.on('controller')
def handle_controller_event(controller_command):
    global robot
    webcommand = json.loads(controller_command)
    command = webcommand.command
    value = webcommand.value    
    robot.sendCommand(command, value)    
    logging.info(command)
    logging.info(value)

@videoapp.route('/video_feed')
def video_feed():
    return Response(gen(appCamera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@videoapp.route('/gallery')
def static_images():
    try:
        lst = os.listdir('static/images/')
        lst = sorted(lst)
    except OSError:
        pass
    return render_template('gallery.html', files = lst, totalfiles = len(lst))

@videoapp.route('/shutdown')
def shutdown():
    global robot
    robot.StopControls()
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return "Shutting down..."

@app.route('/webcontrol')
def web_control():
    return render_template('webcontrol.html', host = get_ip(), port = server_port, videoport = video_port)

#@app.route('/shutdown')
#def shutdown():
#    global robot
#    robot.StopControls()
#    func = request.environ.get('werkzeug.server.shutdown')
#    if func is None:
#        raise RuntimeError('Not running with the Werkzeug Server')
#    func()
#    return "Shutting down..."    

def startVideoThread():
    videoapp.run(host='0.0.0.0', port=video_port)
    

if __name__ == '__main__':
    global appCamera
    global robot
    global videoappThread
    appCamera = vs.VideoStream()
    robot = rbc.Robot_Controller(appCamera)
    robot.StartThisThing()
    
    videoappThread = threading.Thread(target=startVideoThread)
    videoappThread.start()
    socketio.run(app, host='0.0.0.0', port=server_port)
    
    
    
    
