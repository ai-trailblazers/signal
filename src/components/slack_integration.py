import logging

from abc import abstractmethod, ABC
from messages.web_hooks_server_message import WebHooksServerMessage, WebHooksServerMessageType
from messages.slack_integration_message import SlackIntegrationMessage
from reactivex import Observer, subject

class SlackIntegrationObserver(Observer, ABC):
    def on_next(self, message):
        if isinstance(message, WebHooksServerMessage):
            self._processWebHookMessage(message)
        else:
            logging.warn(f"Message '{type(message).__name__}' is not supported")

    def on_error(self, error):
        logging.error(error)

    def on_completed(self):
        logging.debug("Completed")

    @abstractmethod
    def _processWebHookMessage(self, message: WebHooksServerMessage):
        pass

class SlackIntegration(SlackIntegrationObserver):
    def __init__(self):
        super().__init__()
        self.subject = subject.Subject()

    def start(self):
        return self.subject

    def _processWebHookMessage(self, message: WebHooksServerMessage):
        if message.type is WebHooksServerMessageType.SLACK:
            logging.debug(f"Received message '{message.content}' from '{message.from_}'")

            slackIntegrationMessage = SlackIntegrationMessage("mock slack integration message")

            logging.debug("Publishing SlackIntegrationMessage")

            self.subject.on_next(slackIntegrationMessage)
        else:
            logging.warn(f"WebHookMessage type '{message.type}' is not supported")
    