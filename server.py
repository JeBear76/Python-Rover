# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 18:49:36 2019

@author: jerep_000
"""

from flask import Flask, Response, render_template, request
import videostream as vs
import os
import robot_controller as rbc
        
app = Flask(__name__)

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
        lst = sorted(lst)
    except OSError:
        pass

    return render_template('gallery.html', files = lst, totalfiles = len(lst))

@app.route('/shutdown')
def shutdown():
    global appCamera
    global robot
    robot.StopControls()
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return "Shutting down..."    

if __name__ == '__main__':
    global appCamera
    global robot
    appCamera = vs.VideoStream()
    robot = rbc.Robot_Controller(appCamera)
    robot.StartThisThing()
    app.run(host='0.0.0.0', port=3000)
    
    
    
    
