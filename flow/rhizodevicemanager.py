##Handles device connection/disconnetion events by creating or removing/destroying devices.
import os
import threading
from time import sleep
from rhizodevice import RhizoDevice
from eventsmanager import EventsManager

class RhizoDeviceManager():
    def __init__(self):
        self.em = EventsManager()
        self.connectedDevices = {} #dict of port:device

        self.em.subscribe("usb-connect", self.connectionEventHandler)
        self.em.subscribe("usb-disconnect", self.connectionEventHandler)

    def connectionEventHandler(self, event):
        type = event["topic"]
        port = event["port"]
        if(type == "usb-connect"):
            self.addDevice(port)
        elif(type == "usb-disconnect"):
            self.removeDevice(port)

    def addDevice(self, port):
        print("DeviceManager: Creating new device.")
        device = RhizoDevice(port)
        self.connectedDevices[port] = device
        self.em.publish("device-added", {"port":port})

    def removeDevice(self, port):
        print("DeviceManager: Removing device.")
        device = self.connectedDevices.pop(port)
        device.destroy()
        self.em.publish("device-removed", {})
    
    def getComponentIDsList(self):
        list = []
        for port in self.connectedDevices:
            device = self.connectedDevices[port]
            for componentID in device.getComponentIDsList():
                list.append(componentID)
        return list