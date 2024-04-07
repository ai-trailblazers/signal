import logging

from reactivex import Subject, interval
from reactivex.operators import map, start_with
from reactivex.disposable import Disposable
from events.project_status_message import IdentifiedProjectStatusMessage, RespondProjectStatusMessage
from events.urgent_message import IdentifiedUrgentMessage, RespondUrgentMessage

class Slack(Subject):
    def __init__(self):
        super().__init__()
        self.message_scanner: Disposable = None

    def start(self, interval_seconds):
        if self.message_scanner:
            self.message_scanner.dispose()

        self.message_scanner = interval(interval_seconds).pipe(
            start_with(0),
            map(lambda _: self._scan_messages())
        ).subscribe()

    def on_next(self, event):
        if isinstance(event, IdentifiedUrgentMessage):
            self._handle_identified_urgent_message_event(event)
        elif isinstance(event, RespondProjectStatusMessage):
            self._handle_respond_project_status_message_event(event)
        elif isinstance(event, RespondUrgentMessage):
            self._handle_respond_urgent_message_event(event)
        else:
            logging.debug(f"Event '{type(event).__name__}' is not supported.")
    
    def on_error(self, error):
        logging.error(error)

    def stop(self):
        if self.message_scanner:
            self.message_scanner.dispose()
        
        self.dispose()

    def _scan_messages(self):
        # todo : use Langchain Slack toolkit to identify project status messages
        self._scan_project_status_messages()
        
        # todo : use Langchain Slack toolkit to identify urgent messages that need replies
        self._scan_urgent_messages()
    
    def _handle_identified_urgent_message_event(self, event: IdentifiedUrgentMessage):
        logging.debug(f"Handling '{type(event).__name__}'.")
        # Emmit event to respond to an urgent message.
        self.on_next(RespondUrgentMessage())

    def _handle_respond_project_status_message_event(self, event: RespondProjectStatusMessage):
        logging.debug(f"Handling '{type(event).__name__}'.")
    
    def _handle_respond_urgent_message_event(self, event: RespondUrgentMessage):
        logging.debug(f"Handling '{type(event).__name__}'.")

    def _scan_project_status_messages(self):
        logging.debug("Scanning for project status messages.")

        mocked_content = {
            "input": "can you please provide me with a status update of the PD2 project? Cheers.",
            "_from": "Joe Smith"
        }

        super().on_next(IdentifiedProjectStatusMessage(content=mocked_content))

    def _scan_urgent_messages(self):
        logging.debug("Scanning for urgent messages.")
        # Emmit event of a urgent message that has been identified.
        self.on_next(IdentifiedUrgentMessage())
    