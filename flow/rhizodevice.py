#A Rhizo device manages communications with a physical device over a serial connection.
#You can set its data-message-sending interval, and tell it to provide metadata about its components.
#It can generate device messages (some are data, some are metadata).

import threading
from time import sleep
from serialconnection import SerialConnection
from component import Component
from eventsmanager import EventsManager

class RhizoDevice():
    def __init__(self, port):
        print("Device: Initializing myself as a new device on port %s..." % port)
        self.port = port
        self.em = EventsManager()
        self.components = {}  #Dict componentID:component

        self.abort = False
        self.deviceMessageQueue = []
        self.serialConnection = SerialConnection(port, self.addToMessageQueue)
        self.processMessageQueue()

        self.sendCommand({"command":"devices", "params":None}) #request info about what components are on the device
        self.sendCommand({"command":"interval", "params":2}) #sets the data-sending rate to 1 second
        print("Device: Done Initializing.")

    def destroy(self):
        for componentID in self.components:
            self.em.unsubscribe(self.sendCommand)
            self.em.publish("component-removed",{"componentID":componentID})    
        self.serialConnection.closeConnection()
        self.serialConnection = False
        self.abort = True

    def addComponent(self, componentID):
        if not componentID in self.components:
            self.components[componentID] = Component(componentID)
            self.em.publish("component-added",{"componentID":componentID})
            self.em.subscribe("%s/command" % componentID, self.sendCommand)
        self.sendCommand({"command":"%s: info" % componentID, "params": None})  #request info about this component

    def updateComponents(self, componentID, key, value):
        if componentID in self.components:
            self.components[componentID].updateInfo(key, value)
        else:
            self.addComponent(componentID)

    #messaging related methods
    def sendCommand(self, message):
        command = message["command"]
        params = message["params"]
        try:
            if params is not None:
                msg = "%s %s" % (command, params)
                self.serialConnection.writeMessage(msg)
            else:
                msg = command
                self.serialConnection.writeMessage(msg)
        except:
            print("Device: Error sending command over serial connection.")

    # collect messages from the SerialConnection
    def addToMessageQueue(self, message):
        self.deviceMessageQueue.append(message)

    # process incoming serial message queue
    def _processMessageQueue(self):
        while True:
            if not self.abort:
                if len(self.deviceMessageQueue) > 0:
                    msg = self.deviceMessageQueue.pop(0)
                    msg_array = msg.decode('utf-8').split("|")[0].split(" ") # Ugly, but this is just how the messages seem to be formatted: "c:v 492|69100"
                    cmd = msg_array.pop(0).split(":")

                    #Decide what kind of message it was-- either meta:devices [components], or componentId:info_type [value]
                    if cmd[0] == "meta":
                        if cmd[1] == "devices":
                            for component in msg_array:
                                self.addComponent(component)
                    else:
                        if cmd[0] == "nack":
                            print("Device not acknowledging messages")
                            pass
                        if len(cmd) > 1:
                            if cmd[1] == "nack" or cmd[1]== "ack":
                                pass
                            else:
                                comp = cmd[0]
                                key = cmd[1]
                                value = msg_array
                                if key == "v":
                                    key = "state"
                                self.updateComponents(comp, key, value)
                else:
                    pass
            else:
                break

    def processMessageQueue(self):
        t = threading.Thread(target=self._processMessageQueue)
        t.start()