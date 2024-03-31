import logging

from abc import abstractmethod, ABC
from messages.slack_integration_message import SlackIntegrationMessage
from reactivex import Observer

class AIAgentObserver(Observer, ABC):
    def on_next(self, message):
        if isinstance(message, SlackIntegrationMessage):
            self._processSlackMessage(message)
        else:
            logging.warn(f"Message '{type(message).__name__}' is not supported")

    def on_error(self, error):
        logging.error(error)

    def on_completed(self):
        logging.debug("Completed")

    @abstractmethod
    def _processSlackMessage(self, message: SlackIntegrationMessage):
        pass

class AIAgent(AIAgentObserver):
    def __init__(self):
        super().__init__()

    def _processSlackMessage(self, message: SlackIntegrationMessage):
        logging.debug(f"Received SlackIntegrationMessage with content '{message.content}'")