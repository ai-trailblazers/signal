from common.message import Message

class SlackEventMessage(Message):
    def __init__(self, msg="SlackEventMessage"):
        super().__init__()
        self.msg = msg
