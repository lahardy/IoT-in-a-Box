#!/usr/bin/env python
# -*- coding: utf-8 -*-

#TODO: Add config for service provider info
#TODO: Internal events naming and processing (make more MQTT-transparent)? Can EM ever "tell someone what to do?"
#TODO: Have IoTInterfaceManager re-build its list when devices are dis-connected
#TODO: Integrate the camera as a device/component.

import paho.mqtt.client as mqtt

from eventsmanager import EventsManager
from usbportwatcher import USBPortWatcher
from rhizodevicemanager import RhizoDeviceManager
from mqttserviceprovider import MQTTServiceProvider
from iotinterfacemanager import IoTInterfaceManager
from cameracontroller import CameraController
from webserver import WebServer

MQTT_SERVER_ADDRESS = "10.0.0.145"
MQTT_CLIENT_NAME = "RPi-fox"
CAMERA_ENABLED = True

#Internal events manager
#Has subscribe/publish methods
#Processes/routes events in its own thread
em = EventsManager()

#Create object to loop over USB ports and watch for new connection/disconnections
usbPortWatcher = USBPortWatcher(em)
#It generates 'usb-connect' and 'usb-disconnect' events.

#Create object to manage list of connected devices
rhizoDeviceManager = RhizoDeviceManager(em)
#Listens for usb-connect/disconnect events and creates/destroys devices in response
#Generates 'device-added' and 'device-removed' events

"""Camera related things here:
    - CameraController (parallels RhizoDevice)
    - Camera (is a 'Component')
    - IoTComponent
"""
cameraController = CameraController(em, "%s-camera" % MQTT_CLIENT_NAME)
stream = cameraController.getStream()

#Devices that are created manage communication with hardware (e.g. over SerialConnection for a RhizoDevice).
#They create and update the state of Components.

#A Component represents a single sensor, actuator or camera.
#Components have methods for getting metadata and state, and setting state.

##Create object to manage connection to and communications with MQTT server
mqttServiceProvider = MQTTServiceProvider(MQTT_CLIENT_NAME, MQTT_SERVER_ADDRESS)
##Has subscription/publish methods.

#IoTDeviceManager creates an IoT interface for every component provided by the devices
iotInterfaceManager = IoTInterfaceManager(rhizoDeviceManager, em, mqttServiceProvider)
#Listens to component-added and component-removed events to update list

#An IoTInterface watches a set of internal events we want to be broadcast over MQTT
#subscribes to events and publishes to mqttclient.
#Could later essentially implement flow diagrams here.

webServer = WebServer()
