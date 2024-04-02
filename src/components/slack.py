import logging

from reactivex import Subject
from events.project_status_message import IdentifiedProjectStatusMessage, RespondProjectStatusMessage
from events.urgent_message import IdentifiedUrgentMessage, RespondUrgentMessage

class Slack(Subject):
    def __init__(self):
        super().__init__()

    def __handleIdentifiedUrgentMessageEvent(self, event: IdentifiedUrgentMessage):
        logging.debug(f"Handling '{type(event).__name__}'.")
        # Emmit event to respond to an urgent message.
        self.on_next(RespondUrgentMessage())

    def __handleRespondProjectStatusMessageEvent(self, event: RespondProjectStatusMessage):
        logging.debug(f"Handling '{type(event).__name__}'.")
    
    def __handleRespondUrgentMessageEvent(self, event: RespondUrgentMessage):
        logging.debug(f"Handling '{type(event).__name__}'.")

    def __scanProjectStatusMessages(self):
        logging.debug("Scanning for project status messages.")
        # Emmit event of a project status message that has been identified.
        super().on_next(IdentifiedProjectStatusMessage())

    def __scanUrgentMessages(self):
        logging.debug("Scanning for urgent messages.")
        # Emmit event of a urgent message that has been identified.
        self.on_next(IdentifiedUrgentMessage())

    def on_next(self, event):
        if isinstance(event, IdentifiedUrgentMessage):
            self.__handleIdentifiedUrgentMessageEvent(event)
        elif isinstance(event, RespondProjectStatusMessage):
            self.__handleRespondProjectStatusMessageEvent(event)
        elif isinstance(event, RespondUrgentMessage):
            self.__handleRespondUrgentMessageEvent(event)
        else:
            logging.debug(f"Event '{type(event).__name__}' is not supported.")

    def scanMessages(self):
        # todo : use Langchain Slack toolkit to identify project status messages
        self.__scanProjectStatusMessages()
        
        # todo : use Langchain Slack toolkit to identify urgent messages that need replies
        self.__scanUrgentMessages()
    