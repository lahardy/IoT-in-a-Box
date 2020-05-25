import threading
from time import sleep

def singleton(cls):    
    instance = [None]
    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = cls(*args, **kwargs)
        return instance[0]
    return wrapper

def sameFunction(f1, f2):   #used for unsubscribing, remove all subscriptions with a certain handler. Hacky, fix later.
    if hasattr(f1, '__func__'):
        f1 = f1.__func__
    if hasattr(f2, '__func__'):
        f2 = f2.__func__
    return f1 is f2

@singleton
class EventsManager():
    def __init__(self):
        self.subscriptions = {}
        self.eventsQueue = []
        self.run()

    def subscribe(self, topic, handler):
        if topic in self.subscriptions:
            handlers = self.subscriptions[topic]
        else:
            handlers = []
        handlers.append(handler)
        self.subscriptions[topic] = handlers
        print("EventsManager: New subscription to %s" % topic)

    def unsubscribe(self, handler):
        for topic in self.subscriptions:
            handlers = self.subscriptions[topic]
            keep = []
            for h in handlers:
                if sameFunction(h, handler) and h.__self__ == handler.__self__:
                    print("EventsManager: Removing subscription to", topic)
                else:
                    keep.append(h)
            self.subscriptions[topic] = keep 

    def publish(self, event):
        self.eventsQueue.append(event)

    def handleEvents(self):
        while True:
            try:
                handlers = []
                event = self.eventsQueue.pop(0)
                try:
                    handlers = self.subscriptions[event["topic"]]
                    for handler in handlers:
                        handler(event)
                except:
                    pass
            except:
                pass

    def run(self):
        t = threading.Thread(target=self.handleEvents)
        t.start()
