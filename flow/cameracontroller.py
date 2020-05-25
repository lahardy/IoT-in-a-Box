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

#        self.em.publish({"topic":"new-component", "componentID":"Rpi-fox-camera"})

    def getID(self):
        return self.ID

    def getInfo(self):
        return self.info

    def getFrame(self):
        return self.camera.get_frame()

    def saveFrameToFile(self, file):
        my_file = open(file, 'wb')
        my_file.write(self.getFrame())
        my_file.close()
        print("Image saved successfully to", file)

    def sendCommand(self, command, params):
         self.commandQueue.append([command, params])

    def _processCommandQueue(self):
        while True:
            if len(self.commandQueue) > 0:
                item = self.commandQueue.pop(0)
                command = item[0]
                params = item[1]
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



"""        

        elif payload['command'] == 'timelapse':
                output = payload['output']
                number = payload['number']
                seconds_delay = payload['seconds_delay']

                #make folder 'output' to hold images
                print("Timelapse images stored in folder " + output)
                if not os.path.exists(output):
                        os.makedirs(output)     
        
                for x in range(0, number):
                        print("Taking photo number %d" % x)
                        take_still("./{}/timelapse_image_{}.jpg".format(output,x))
                        sleep(seconds_delay) 
                print("Timelapse complete!")            

        elif payload['command'] == "video":
                duration = payload['duration']
                output = payload['output']
                take_video(duration, output)

        elif payload['command'] == "stop":
                camera.close()


    def send_stream(self):
        while True:
            try:
                if self.next_status == True and self.current_status == False:
                    self.camera.start_recording(self.stream, format='mjpeg')
                    self.current_status = True
                if self.next_status == False and self.current_status == True:
                    self.camera.stop_recording()
                    self.current_status = False
                sleep(.1)
            except:
                print("Error!")
            finally:
                pass



class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = threading.Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

"""
