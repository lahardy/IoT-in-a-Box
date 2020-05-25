import serial
import threading
import logging
from time import sleep

def crc16_update(crc, data):
    data = data ^ (crc & 0xFF)
    data = data ^ ((data << 4) & 0xFF)
    return (((data << 8) & 0xFFFF) | ((crc >> 8) & 0xFF)) ^ (data >> 4) ^ (data << 3)

# an implementation of the CRC16-CCITT algorithm; assumes message is an ascii string
def crc16_ccitt(message):
    crc = 0xFFFF
    for c in message:
        crc = crc16_update(crc, ord(c))
    return crc



class SerialConnection():
    def __init__(self, port, handler):
        self.port = port
        self.handleSerialMessage = handler
        self.abort = False
        self.connected = False
        self.connection = self.openConnection(port, baud_rate=9600)
        self.startReading()

    # open a new serial connection
    def openConnection(self, port, baud_rate):
        while not self.connected and not self.abort:
            try:
                connection = serial.Serial(port, baudrate = baud_rate, timeout = 0.05)
                self.connected = True
                return connection
            except Exception as e:
                print('SerialConnection: unable to connect on port', e)
                sleep(1)

    # close a serial connection
    def closeConnection(self):
        self.abort = True
        self.connection.close()
        self.connected = False

    # write a command to the serial port; adds a checksum
    def writeMessage(self, message):
        crc = crc16_ccitt(message)
        try:
            data = bytes('%s|%d\n' % (message, crc), 'utf-8')
            self.connection.write(data)
        except Exception as e:
            print("ERROR: SerialConnection, error while writting serial message", e)

    # read a message from the serial port
    def readMessages(self):
        while True:
            if not self.abort:
                message = None
                try:
                    if self.connection.inWaiting() > 0:
                        try:
                            message = self.connection.readline()
                            self.handleSerialMessage(message)
                        except Exception as e:
                            print("ERROR: SerialConnection: Serial Exception while reading serial message", e)
                    else: 
                        sleep(.1)
                except Exception as e:
                    print("ERROR: SerialConnection: Probably because connection is disrupted", e)
                    sleep(1)
            else:
                break

    def startReading(self):
        self.t = threading.Thread(target=self.readMessages)
        self.t.start()
