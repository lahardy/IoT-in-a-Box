##Loops in thread looking for usb devices on serial ports. Maintains a list of connected ports.
import os
import threading
import json
from time import sleep
from eventsmanager import EventsManager

class USBPortWatcher():
    def __init__(self):
        self.em = EventsManager()
        self.connectedUSBPorts = []
        self.run()

    def getUSBPorts(self):
        return self.connectedUSBPorts

    def watch_usb(self):
        prev_usb_ports = []
        while True:

            # get list of usb ports with connections
            if os.path.exists('/dev/'):
                all_ports = os.listdir('/dev')
            else:
                all_ports = []
            usb_ports = [port_name for port_name in all_ports if (port_name.startswith('ttyUSB') or port_name.startswith('ttyACM'))]

            # look for new usb connections
            for short_port_name in usb_ports:
                if not short_port_name in prev_usb_ports:
                    port = '/dev/' + short_port_name
                    print("USBWatcher: New device found on port", port)
                    event = {"topic":"usb-connect","port":port}
                    self.em.publish(event)

            # look for usb disconnections
            for short_port_name in prev_usb_ports:
                if not short_port_name in usb_ports:
                    port = '/dev/' + short_port_name
                    print("USBWatcher: Device removed from port", port)
                    event = {"topic":"usb-disconnect","port":port}
                    self.em.publish(event)

            # save list for next pass around
            prev_usb_ports = usb_ports
            self.connectedUSBPorts = usb_ports
            sleep(.2)

    def run(self):
        t = threading.Thread(target=self.watch_usb)
        t.start()
