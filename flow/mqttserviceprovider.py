#Manages connection to MQTT server.
#Handles subscriptions/publishing to server.

import paho.mqtt.client as mqtt
import json
import threading

def sameFunction(f1, f2):   #used for unsubscribing, remove all subscriptions with a certain handler. Hacky, fix later.
    if hasattr(f1, '__func__'):
        f1 = f1.__func__
    if hasattr(f2, '__func__'):
        f2 = f2.__func__
    return f1 is f2

class MQTTServiceProvider:
    def __init__(self, clientName, serverAddress):
        self.client = mqtt.Client(clientName)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.connect(serverAddress)

        self.subscriptions = {}
        self.run()

    def on_connect(self, client, userdata, flags, rc):
        print("MQTTServiceProvider: Connected to MQTT server. Ready to subscribe and publish!")

    def on_message(self, client, userdata, msg):
        payload_str = msg.payload.decode('utf-8')
        payload = json.loads(payload_str)
        payload["topic"] = msg.topic

        print("MQTT IN: TOPIC: %s and MESSAGE w/topic re-inserted: %s" % (msg.topic, payload))
        handlers = self.subscriptions[msg.topic]
        for handler in handlers:
            handler(payload)

    def on_publish(self, client, userdata, res):
        pass

    #Need to connect this to topic:handler
    def subscribe(self, topic, handler):
        self.client.subscribe(topic)
        if topic not in self.subscriptions:
            self.subscriptions[topic] = [handler]
        else:
            current_handlers = self.subscriptions[topic]
            if handler not in set(current_handlers):
                current_handlers.append(handler)

    def unsubscribe(self, handler):
        for topic in self.subscriptions:
            handlers = self.subscriptions[topic]
            keep = []
            for h in handlers:
                if sameFunction(h, handler) and h.__self__ == handler.__self__:
                    print("MQTT: Removing subscription to", topic)
                else:
                    keep.append(h)
            self.subscriptions[topic] = keep

    def publish(self, topic, msg):
        msg_str = json.dumps(msg).encode('utf-8')
        try:
            self.client.publish(topic, msg_str)
        except Exception as e:
            print("ERROR:", e)

        print("MQTT OUT: TOPIC: %s and MESSAGE: %s" % (topic, msg_str))

    def run(self):
        t = threading.Thread(target=self.client.loop_forever)
        t.start()