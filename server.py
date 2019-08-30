# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 18:49:36 2019

@author: jerep_000
"""

from flask import Flask, Response, render_template, request, send_from_directory

from flask_socketio import SocketIO
from flask_cors import CORS
import json

import os
import socket

import videostream as vs
import threading

#import robot_controller as rbc

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

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        
server_port = 3000
video_port = 3001   
videoapp = Flask('videoApp')

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
    global appCamera
    global robot
#    robot.StopControls()
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    appCamera.stop_stream()
    socketio.stop()
    return "Shutting down..."

@videoapp.route('/webcontrol')
def web_control():
    return render_template('webcontrol.html', host = get_ip(), port = server_port, videoport = video_port)

@videoapp.route('/favicon.ico') 
def favicon():
    return send_from_directory(os.path.join(videoapp.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

def startVideoThread():
    videoapp.run(host='0.0.0.0', port=video_port)

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretKey'
socketio = SocketIO(app = app, kwargs = { 'cors_allowed_origin' : '*' })

@socketio.on('connection', namespace='io')
def handle_connection():
    print('Client connected')

@socketio.on('event', namespace='io')
def handle_event(message):
    print(message)
    socketio.emit('message', message)

@socketio.on('controller', namespace='io')
def handle_controller_event(controller_command):
    global robot
    webcommand = json.loads(controller_command)
    command = webcommand.command
    value = webcommand.value    
#    robot.sendCommand(command, value) 
    socketio.emit('message', 'command: ' +  command + ' received ' + str(value))


    
if __name__ == '__main__':
    global appCamera
    global robot
    global videoappThread
    appCamera = vs.VideoStream()
#    robot = rbc.Robot_Controller(appCamera)
#    robot.StartThisThing()
    
    videoappThread = threading.Thread(target=startVideoThread)
    videoappThread.start()
    socketio.run(app, host='0.0.0.0', port=server_port)
    
    
    
    
