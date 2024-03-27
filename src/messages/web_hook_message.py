from common.message import Message

class WebHookMessage(Message):
    def __init__(self, msg="WebHookMessage"):
        super().__init__()
        self.msg = msg