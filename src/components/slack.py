import logging

from reactivex import Subject, interval
from reactivex.operators import map
from events.project_status_message import IdentifiedProjectStatusMessage, RespondProjectStatusMessage
from events.urgent_message import IdentifiedUrgentMessage, RespondUrgentMessage

class Slack(Subject):
    def __init__(self):
        super().__init__()
        self.message_scanner_disposable = None

    def on_next(self, event):
        if isinstance(event, IdentifiedUrgentMessage):
            self.__handle_identified_urgent_message_event(event)
        elif isinstance(event, RespondProjectStatusMessage):
            self.__handle_respond_project_status_message_event(event)
        elif isinstance(event, RespondUrgentMessage):
            self.__handle_respond_urgent_message_event(event)
        else:
            logging.debug(f"Event '{type(event).__name__}' is not supported.")
    
    def on_error(self, error):
        logging.error(error)

    def start(self, interval_seconds):
        if self.message_scanner_disposable:
            self.message_scanner_disposable.dispose()

        self.message_scanner_disposable = interval(interval_seconds).pipe(
            map(lambda _: self.__scan_messages())
        ).subscribe()

    def stop(self):
        if self.message_scanner_disposable:
            self.message_scanner_disposable.dispose()
        
        self.dispose()

    def __scan_messages(self):
        # todo : use Langchain Slack toolkit to identify project status messages
        self.__scan_project_status_messages()
        
        # todo : use Langchain Slack toolkit to identify urgent messages that need replies
        self.__scan_urgent_messages()
    
    def __handle_identified_urgent_message_event(self, event: IdentifiedUrgentMessage):
        logging.debug(f"Handling '{type(event).__name__}'.")
        # Emmit event to respond to an urgent message.
        self.on_next(RespondUrgentMessage())

    def __handle_respond_project_status_message_event(self, event: RespondProjectStatusMessage):
        logging.debug(f"Handling '{type(event).__name__}'.")
    
    def __handle_respond_urgent_message_event(self, event: RespondUrgentMessage):
        logging.debug(f"Handling '{type(event).__name__}'.")

    def __scan_project_status_messages(self):
        logging.debug("Scanning for project status messages.")
        # Emmit event of a project status message that has been identified.
        super().on_next(IdentifiedProjectStatusMessage())

    def __scan_urgent_messages(self):
        logging.debug("Scanning for urgent messages.")
        # Emmit event of a urgent message that has been identified.
        self.on_next(IdentifiedUrgentMessage())
    