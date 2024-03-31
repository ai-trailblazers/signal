import logging

from reactivex import Subject
from events.web_hook import WebHookEvent, WebHookEventType
from events.slack import SlackEvent

class SlackIntegration(Subject):
    def __init__(self):
        super().__init__()

    def processWebHookEvent(self, event: WebHookEvent):
        if event.type is WebHookEventType.SLACK:
            logging.debug(f"Received event '{event.content}' from '{event.from_}'")

            slackEvent = SlackEvent("mock slack event")

            self.on_next(slackEvent)
        else:
            logging.warn(f"WebHookEventType '{event.type}' is not supported")
    