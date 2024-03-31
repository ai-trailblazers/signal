from reactivex import subject

from events.web_hook import WebHookEvent

class WebHooksServer:
    def __init__(self):
        self.subject = subject.Subject()

    def start(self):
        return self.subject
    
    def http_request_received(self, event: WebHookEvent):
        self.subject.on_next(event)
