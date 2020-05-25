from eventsmanager import EventsManager

class Component():
    def __init__(self, id, sendCommand):
        self.id = id
        self.info = {}
        self.sendCommand = sendCommand
        self.em = EventsManager()

    def getID(self):
        return self.id

    def getInfo(self):
        return self.info

    def updateInfo(self, key, value):
        self.info[key] = value
        if key == "state":
            message = {"topic": "%s/update" % self.id, "value": value}
            self.em.publish(message)
