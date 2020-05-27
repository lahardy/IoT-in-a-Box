import threading
import json
from time import sleep
from eventsmanager import EventsManager
from iotinterface import IoTInterface

class IoTInterfaceManager():
    def __init__(self, mqttService):
        self.mqttService = mqttService
        self.em = EventsManager()
        self.interfaces = {}

        #get notified when components are added/removed
        self.em.subscribe("component-added", self.onComponentAdded)
        self.em.subscribe("component-removed", self.onComponentRemoved)

    def createInterface(self, componentID):
        self.interfaces[componentID] = IoTInterface(componentID, self.mqttService)

    def onComponentAdded(self, event):
        #create a new IoTInterface for each component, to subscribe to that component's topics
        componentID = event["componentID"]
        if not componentID in self.interfaces:
            self.createInterface(componentID)

    def onComponentRemoved(self, event):
        #destroy IoTInterfaces for each component
        componentID = event["componentID"]
        interface = self.interfaces.pop(componentID)
        interface.destroy()