from messages.web_hooks_server_message import WebHooksServerMessage
from reactivex import subject

class WebHooksServer:
    def __init__(self):
        self.subject = subject.Subject()

    def start(self):
        return self.subject
    
    def http_request_received(self, message: WebHooksServerMessage):
        self.subject.on_next(message)
