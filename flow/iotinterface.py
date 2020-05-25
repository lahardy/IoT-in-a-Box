#Internally subscribes to changes in that component, sends them out
#Externally subscribes to componentID/* and parses/sends to component as command/value

##TODO: Maybe just get the componentID and pass queries to it rather than  keeping the component itself around.
##TODO: Re-consider having "announce" be this special method type. Consider having "acknowledge" be something more like "response" or "success"

from eventsmanager import EventsManager

class IoTInterface():
    def __init__(self, component, mqttProvider):
        self.component = component
        self.componentInfo = component.getInfo()
        self.em = EventsManager()
        self.mqtt = mqttProvider

	#subscribe to external/MQTT events to send in
        self.mqtt.subscribe("roll-call/who-there", self.announce)

        #announce yourself
        msg = {"name":self.component.getID(), "info":self.component.getInfo()}
        self.mqtt.publish("roll-call/hello", msg)

        #receive commands addressed to this component
        topic = "%s/command" % self.component.getID()
        self.mqtt.subscribe(topic, self.processIncomingMessage)

        #subscribe to internal events to send out
        topic = "%s/update" % self.component.getID()
        self.em.subscribe(topic, self.processOutgoingMessage)

    def destroy(self):
        #unsubscribe before I get destroyed.
        self.em.unsubscribe(self.processOutgoingMessage)

        msg = {"name":self.component.getID(), "info":self.component.getInfo()}
        self.mqtt.publish("roll-call/goodbye", msg)
        self.mqtt.unsubscribe(self.announce)
        self.mqtt.unsubscribe(self.processIncomingMessage)

    def announce(self, message):
        msg = {"name":self.component.getID(), "info":self.component.getInfo()}
        self.mqtt.publish("roll-call/response", msg)

    def processOutgoingMessage(self, message):
        topic = message.pop("topic")  #Separate the message and topic to format for MQTT server
        self.mqtt.publish(topic, message)

    def processIncomingMessage(self, message):
        #parse the message content for command
        command = message["command"]
        params = message["params"]
        self.component.sendCommand(command, params)

        #acknowledge
        topic = "%s/response" % message["topic"]
        msg = {"response":"ack"}
        self.mqtt.publish(topic, msg)
