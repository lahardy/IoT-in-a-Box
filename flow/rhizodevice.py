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

        self.sendCommand("devices", None) #request info about what components are on the device
        self.sendCommand("interval", 2) #sets the data-sending rate to 1 second
        print("Device: Done Initializing.")

    def destroy(self):
        for componentID in self.components:
            self.em.publish({"topic":"component-removed","componentID":componentID})    
        self.serialConnection.closeConnection()
        self.serialConnection = False
        self.abort = True

    def addComponent(self, component_name):
        componentID = "%s/%s" % (self.port, component_name)
        if not componentID in self.components:
            self.components[componentID] = Component(componentID, self.sendCommand)
            self.em.publish({"topic":"component-added","componentID":componentID})
        self.sendCommand("%s: info" % component_name, None)  #request info about this component

    def updateComponents(self, component_name, key, value):
        componentID = "%s/%s" % (self.port, component_name)
        if componentID in self.components:
            self.components[componentID].updateInfo(key, value)
        else:
            self.addComponent(component_name)

    def getComponentByID(self, componentID):
        result = False
        if componentID in self.components:
            result = self.components[componentID]
        return result

    def getComponentIDsList(self):
        list = []
        for componentID in self.components:
            list.append(componentID)
        return list

    #messaging related methods
    def sendCommand(self, command, value):
        try:
            if value is not None:
                msg = "%s %s" % (command, value)
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
