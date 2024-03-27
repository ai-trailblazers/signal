from common.observer import Observer

class Message():
    def handle(self, observer: Observer):
        observer.handle_message(self)
