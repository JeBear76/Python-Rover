# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 18:49:36 2019

@author: jerep_000
"""
from flask import Flask, Response, render_template, request, send_from_directory
from gevent.pywsgi import WSGIServer

import socketio
import json

import os
import socket

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

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

prev_sid = None
server_port = 3000
video_port = 3001

videoapp = Flask('videoApp')
mainapp = Flask(__name__)

sio = socketio.Server(async_mode='threading', cors_allowed_origins = '*');
mainapp.wsgi_app = socketio.WSGIApp(sio, mainapp.wsgi_app)

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
    robot.StopControls()
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    appCamera.stop_stream()
    return "Shutting down..."

@videoapp.route('/webcontrol')
def web_control():
    return render_template('webcontrol.html', host = get_ip(), port = server_port, videoport = video_port)

@videoapp.route('/favicon.ico') 
def favicon():
    return send_from_directory(os.path.join(videoapp.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

def startMainThread():
    mainapp.run(host='0.0.0.0', port=server_port, threaded = True)

@sio.event
def connect(sid, environ):
    global prev_sid
    if prev_sid != sid:
        sio.disconnect(prev_sid)
        prev_sid = sid
        print('\x1b[1;31;40mClient connected' + '\x1b[0m')        

@sio.event
def disconnect(sid):
    print('\x1b[1;31;40mClient disconnected' + '\x1b[0m')

@sio.on('event')
def handle_event(sid, message):
    print('\x1b[1;36;40m' + message + '\x1b[0m')
    sio.send(sid, 'message', message)

@sio.on('controller')
def handle_controller_event(sid, controller_command):
    global robot
    webcommand = json.loads(controller_command)
    print('\x1b[1;36;40m' + controller_command + '\x1b[0m')
    command = webcommand['command']
    value = webcommand['value']
    robot.sendCommand(command, value, False) 
    sio.send(sid, 'message', 'command: ' +  command + ' received ' + str(value))


#    global appCamera
#    global robot
#    global mainappThread
print('\x1b[1;31;40m' + get_ip() + '\x1b[0m')
appCamera = vs.VideoStream()
robot = rbc.Robot_Controller(appCamera)
robot.StartThisThing()

mainappThread = threading.Thread(target=startMainThread)
mainappThread.start()

if __name__ == '__main__':    
    videoapp.run(host='0.0.0.0', port=video_port)
    videoapp.debug = True
    WSGIServer(('', video_port), videoapp).serve_forever()

