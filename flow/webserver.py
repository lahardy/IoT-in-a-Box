#!/usr/bin/env python
from flask import Flask, send_from_directory, Response
from camera import Camera
from time import sleep

def gen(get_frame):
    while True:
        frame = get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

class EndpointAction(object):
    def __init__(self, action):
        self.action = action
        self.response = Response(status=200, headers={})

    def __call__(self, *args):
        return self.action(args)

class WebServer(object):
    def __init__(self, name, get_frame):
        self.app = Flask(name)
        self.get_frame = get_frame
        self.add_endpoint(endpoint='/', endpoint_name='home', handler=self.index)
        self.add_endpoint('/index.html', 'index', self.index)
        self.add_endpoint('/stream.mjpg', 'video_feed', self.stream_video)

    def index(self, args):
        return send_from_directory('static', 'index.html')

    def stream_video(self, args):
        return Response(gen(self.get_frame), mimetype='multipart/x-mixed-replace; boundary=frame')

    def add_endpoint(self, endpoint, endpoint_name, handler):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler))

    def run(self):
        self.app.run(host='0.0.0.0', port=8000)