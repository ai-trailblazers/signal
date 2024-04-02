import logging

from reactivex import Subject
from events.project_status_message import IdentifiedProjectStatusMessage, RespondProjectStatusMessage

class Jira(Subject):
    def __init__(self):
        super().__init__()

    def on_next(self, event):
        if isinstance(event, IdentifiedProjectStatusMessage):
            self.__handleIdentifiedProjectStatusMessageEvent(event)
        else:
            logging.debug(f"Event '{type(event).__name__}' is not supported.")

    def on_error(self, error):
        logging.error(error)

    def __handleIdentifiedProjectStatusMessageEvent(self, event: IdentifiedProjectStatusMessage):
        logging.debug(f"Handling '{type(event).__name__}' event.")
        
        # todo : use Langchain Jira toolkit to compose a status report
        mockRespondProjectStatusMessage = RespondProjectStatusMessage()

        logging.debug(f"Emmiting '{type(mockRespondProjectStatusMessage).__name__}' event.")

        # Emmit event to respond to a project status message.
        super().on_next(mockRespondProjectStatusMessage)
