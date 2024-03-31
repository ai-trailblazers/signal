import logging

from abc import abstractmethod, ABC
from reactivex import Observer

from events.slack import SlackEvent

class AIAgentObserver(Observer, ABC):
    def on_next(self, event):
        if isinstance(event, SlackEvent):
            self._processSlackEvent(event)
        else:
            logging.debug(f"Event '{type(event).__name__}' is not supported")

    def on_error(self, error):
        logging.error(error)

    def on_completed(self):
        logging.debug("Completed")

    @abstractmethod
    def _processSlackEvent(self, event: SlackEvent):
        pass

class AIAgent(AIAgentObserver):
    def __init__(self):
        super().__init__()

    def _processSlackEvent(self, event: SlackEvent):
        logging.debug(f"Received SlackEvent with content '{event.content}'")