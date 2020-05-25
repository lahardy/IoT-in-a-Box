#creates an IoTInterface for each component
#e.g. makes each sensor available as an "IoT sensor"
import threading
import json
from time import sleep
from eventsmanager import EventsManager
from iotinterface import IoTInterface

class IoTInterfaceManager():
    def __init__(self, deviceManager, mqttService):
        self.deviceManager = deviceManager
        self.em = EventsManager()
        self.mqttService = mqttService

        #get notified when components are added/removed
        self.em.subscribe("component-added", self.onComponentAdded)
        self.em.subscribe("component-removed", self.onComponentRemoved)

        self.interfaces = {}
        list = self.deviceManager.getComponentIDsList()
        for componentID in list:
            self.createInterface(componentID)

    def createInterface(self, componentID):
        component = self.deviceManager.getComponentByID(componentID)
        self.interfaces[componentID] = IoTInterface(component, self.mqttService)

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
