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
        event = {"topic":"device-added", "port": port}
        self.em.publish(event)

    def removeDevice(self, port):
        print("DeviceManager: Removing device.")
        device = self.connectedDevices.pop(port)
        device.destroy()
        event = {"topic":"device-removed"}
        self.em.publish(event)

##For providing components/info
    def getComponentByID(self, componentID):
        component = False
        for port in self.connectedDevices:
            device = self.connectedDevices[port]
            result = device.getComponentByID(componentID)
            if result:
                component = result
                break
        return component

    def getComponentIDsList(self):
        list = []
        for port in self.connectedDevices:
            device = self.connectedDevices[port]
            for componentID in device.getComponentIDsList():
                list.append(componentID)
        return list
