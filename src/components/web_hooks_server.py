from messages.web_hook_message import WebHookMessage
from reactivex import create, Observer

class WebHooksServer:
    def __init__(self):
        self.observer: Observer = None

    def start(self):
        def on_subscribe(observer: Observer, _):
            self.observer = observer
        return create(on_subscribe)
    
    def http_request_received(self, data):
        if self.observer:
            message = WebHookMessage()
            self.observer.on_next(message)
    