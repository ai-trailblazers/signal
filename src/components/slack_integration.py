from messages.slack_event_message import SlackEventMessage
from abc import abstractmethod, ABC
from common.observer import Observer

class SlackIntegration(Observer, ABC):
    def __init__(self):
        super().__init__()

    def handle_message(self, message: SlackEventMessage):
        print(message.msg)