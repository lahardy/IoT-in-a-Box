#Internally subscribes to changes in that component, sends them out
#Externally subscribes to componentID/* and parses/sends to component as command/value

from eventsmanager import EventsManager

class IoTInterface():
    def __init__(self, componentID, mqttProvider):
        self.componentID = componentID
        self.mqtt = mqttProvider
        self.em = EventsManager()

	    #subscribe to external/MQTT events to send in
        self.mqtt.subscribe("roll-call/who-there", self.announce)

        #receive commands addressed to this component
        topic = "%s/command" % self.componentID
        self.mqtt.subscribe(topic, self.processIncomingMessage)

        #subscribe to internal updates to send out
        topic = "%s/update" % self.componentID
        self.em.subscribe(topic, self.processOutgoingMessage)

        #subscribe to internal info to send out
        topic = "%s/info" % self.componentID
        self.em.subscribe(topic, self.processOutgoingMessage)

        #announce yourself
        msg = {"name":self.componentID}
        self.mqtt.publish("roll-call/hello", msg)

        #tell device to send its info
        self.em.publish("%s/info-request" % self.componentID, {})

    def destroy(self):
        #unsubscribe before I get destroyed.
        self.em.unsubscribe(self.processOutgoingMessage)

        msg = {"name":self.componentID}
        self.mqtt.publish("roll-call/goodbye", msg)
        self.mqtt.unsubscribe(self.announce)
        self.mqtt.unsubscribe(self.processIncomingMessage)

    def announce(self, message):
        msg = {"name":self.componentID}
        self.mqtt.publish("roll-call/response", msg)
        self.em.publish("%s/info-request" % self.componentID, {})

    def processOutgoingMessage(self, message):
        topic = message.pop("topic")  #Separate the message and topic to format for MQTT server
        self.mqtt.publish(topic, message)

    def processIncomingMessage(self, message):
        topic = message.pop("topic")
        self.em.publish(topic, message)

        #acknowledge
        topic = "%s/response" % message["topic"]
        msg = {"response":"ack"}
        self.mqtt.publish(topic, msg)