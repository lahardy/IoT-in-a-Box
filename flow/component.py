from eventsmanager import EventsManager

class Component():
    def __init__(self, id):
        self.id = id
        self.info = {}
        self.em = EventsManager()
        self.em.subscribe("%s/info-request" % self.id, self.getInfo)

    def getInfo(self, message):
        self.em.publish("%s/info" % self.id, {"info": self.info})

    def updateInfo(self, key, value):
        self.info[key] = value
        if key == "state":
            self.em.publish("%s/update" % self.id, {"value": value})