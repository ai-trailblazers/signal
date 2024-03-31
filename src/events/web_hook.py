from enum import Enum

class WebHookEventType(Enum):
    SLACK = "Slack"

class WebHookEvent:
    def __init__(self, type: WebHookEventType, from_: str, content):
        super().__init__()
        self.type = type
        self.from_ = from_
        self.content = content