import logging

from abc import abstractmethod, ABC
from reactivex import Observer, subject

from events.web_hook import WebHookEvent, WebHookEventType
from events.slack import SlackEvent

class SlackIntegrationObserver(Observer, ABC):
    def on_next(self, event):
        if isinstance(event, WebHookEvent):
            self._processWebHookEvent(event)
        else:
            logging.warn(f"Event '{type(event).__name__}' is not supported")

    def on_error(self, error):
        logging.error(error)

    def on_completed(self):
        logging.debug("Completed")

    @abstractmethod
    def _processWebHookEvent(self, event: WebHookEvent):
        pass

class SlackIntegration(SlackIntegrationObserver):
    def __init__(self):
        super().__init__()
        self.subject = subject.Subject()

    def start(self):
        return self.subject

    def _processWebHookEvent(self, event: WebHookEvent):
        if event.type is WebHookEventType.SLACK:
            logging.debug(f"Received event '{event.content}' from '{event.from_}'")

            slackEvent = SlackEvent("mock slack event")

            self.subject.on_next(slackEvent)
        else:
            logging.warn(f"WebHookEventType '{event.type}' is not supported")
    