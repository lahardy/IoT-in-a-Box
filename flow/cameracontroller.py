#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import picamera
import threading
from time import sleep
from camera import Camera
from eventsmanager import EventsManager

class CameraController:
    def __init__(self):
        self.em = EventsManager()
        self.camera = Camera()
        self.ID = "Rpi-Fox-camera"
        self.info = {"info":"dummy"}
        self.commandQueue = []
        self.run()

        self.em.subscribe("%s/command" % self.ID, self.sendCommand)
        self.em.subscribe("%s/info-request" % self.ID, self.getInfo)
        self.em.publish("component-added", {"componentID":self.ID})

    def getInfo(self, message):
        self.em.publish("%s/info" % self.ID, {"info": self.info})

    def getFrame(self):
        return self.camera.get_frame()

    def saveFrameToFile(self, file):
        my_file = open(file, 'wb')
        my_file.write(self.getFrame())
        my_file.close()
        print("Image saved successfully to", file)

    def sendCommand(self, message):
        self.commandQueue.append(message)

    def _processCommandQueue(self):
        while True:
            if len(self.commandQueue) > 0:
                item = self.commandQueue.pop(0)
                command = item["command"]
                params = item["params"]
                if command == "take-photo":
                    file = "/home/pi/IotBox/files/%s" % params['name']
                    self.saveFrameToFile(file)
                elif command == "timelapse":
                    name = params['name']
                    number = params['number']
                    seconds_delay = params['seconds_delay']

                    #make folder 'output' to hold images
                    folder = "/home/pi/IotBox/files/%s" % name 
                    print("Timelapse images stored in %s" % folder)
                    if not os.path.exists(folder):
                        os.makedirs(folder)

                    for x in range(0, number):
                        print("TODO: Taking photo number %d" % x)
                        self.saveFrameToFile("{}/image_{}.jpg".format(folder,x))
                        sleep(seconds_delay)
                    print("Timelapse complete!")
                else:
                    print("Unknown command!")

    def run(self):
        t = threading.Thread(target=self._processCommandQueue)
        t.start()