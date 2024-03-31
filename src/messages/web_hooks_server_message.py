from enum import Enum

class WebHooksServerMessageType(Enum):
    SLACK = "Slack"

class WebHooksServerMessage:
    def __init__(self, type: WebHooksServerMessageType, from_: str, content):
        super().__init__()
        self.type = type
        self.from_ = from_
        self.content = content