#!/usr/bin/env python
# -*- coding: utf-8 -*-

#TODO: Add config for service provider info

import sys
sys.path.append('./flow')

from eventsmanager import EventsManager
from usbportwatcher import USBPortWatcher
from rhizodevicemanager import RhizoDeviceManager
from mqttserviceprovider import MQTTServiceProvider
from iotinterfacemanager import IoTInterfaceManager
from iotinterface import IoTInterface
from cameracontroller import CameraController
from webserver import WebServer
from time import sleep

MQTT_SERVER_ADDRESS = "localhost"
MQTT_CLIENT_NAME = "RPi-fox"
WEBSERVER_NAME = "testserver"

#Internal events manager singleton, gets created first time it is called
#Has subscribe/publish methods
#Processes/routes events in its own thread

##Create object to manage connection to and communications with MQTT server
mqttServiceProvider = MQTTServiceProvider(MQTT_CLIENT_NAME, MQTT_SERVER_ADDRESS)
##Has subscription/publish methods.

#Create object to manage list of connected devices
rhizoDeviceManager = RhizoDeviceManager()
#Listens for usb-connect/disconnect events and creates/destroys devices in response
#Generates 'device-added' and 'device-removed' events


#Devices that are created manage communication with hardware (e.g. over SerialConnection for a RhizoDevice).
#They create and update the state of Components.
#A Component represents a single sensor, actuator or camera.
#Components have methods for getting metadata and state, and setting state.

#IoTDeviceManager creates an IoT interface for every component provided by the devices
iotInterfaceManager = IoTInterfaceManager(mqttServiceProvider)
#Listens to component-added and component-removed events to update list

#An IoTInterface watches a set of internal events we want to be broadcast over MQTT
#subscribes to events and publishes to mqttclient.

cameraController = CameraController()

#Create object to loop over USB ports and watch for new connection/disconnections
usbPortWatcher = USBPortWatcher()
#It generates 'usb-connect' and 'usb-disconnect' events.

webserver = WebServer(WEBSERVER_NAME, cameraController.getFrame)
webserver.run() #takes over the main thread
