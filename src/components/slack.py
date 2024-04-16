import logging

from typing import cast
from reactivex import Subject, interval
from reactivex.operators import map, start_with
from flask import Flask, request, jsonify
from events.project_status_message import IdentifiedProjectStatusMessage, RespondProjectStatusMessage
from events.urgent_message import IdentifiedUrgentMessage, RespondUrgentMessage

class Slack(Subject):
    def __init__(self):
        super().__init__()
        self.server = Flask(__name__)
        self._configure_routes()

    def _configure_routes(self):
        self.server.add_url_rule("/slack/events", self._handle_slack_web_hook_event.__name__, self._handle_slack_web_hook_event, methods=["POST"])
    
    def _handle_slack_web_hook_event(self):
        if not request.is_json:
            return badRequest("Request must contain JSON data.")
        
        return self._scan_message(request.get_json())

    def start(self):
        self.server.run(debug=True, port=5000)

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

    def _scan_message(self, message):
        if 'message' not in message:
            return badRequest("JSON data must contain a 'message' attribute.")
        
        if 'from' not in message:
            return badRequest("JSON data must contain a 'from' attribute.")
        pass
    
    def _handle_identified_urgent_message_event(self, event: IdentifiedUrgentMessage):
        logging.debug(f"Handling '{type(event).__name__}'.")
        
        # Emmit event to respond to an urgent message.
        self.on_next(RespondUrgentMessage())

    def _handle_respond_project_status_message_event(self, event: RespondProjectStatusMessage):
        logging.debug(f"Handling '{type(event).__name__}'.")
    
    def _handle_respond_urgent_message_event(self, event: RespondUrgentMessage):
        logging.debug(f"Handling '{type(event).__name__}'.")

def ok(message="success"):
    return jsonify({
        "message": message
    }), 200

def badRequest(error: str):
    return jsonify({"error": error}), 400
    