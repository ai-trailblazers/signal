import logging
import json

from . import Agent, OPEN_AI_MODEL
from flask import Flask, request, jsonify
from langchain import hub
from langchain_openai import ChatOpenAI
from events.project_status_message import IdentifiedProjectStatusMessage, RespondProjectStatusMessage
from events.urgent_message import IdentifiedUrgentMessage, RespondUrgentMessage

class Slack(Agent):
    def __init__(self):
        super().__init__()
        self.server = Flask(__name__)
        self._configure_routes()

    def _configure_routes(self):
        self.server.add_url_rule("/slack/events", self._handle_slack_web_hook_event.__name__, self._handle_slack_web_hook_event, methods=["POST"])
    
    def _handle_slack_web_hook_event(self):
        if not request.is_json:
            return _bad_request("Request must contain JSON data.")
        
        return self._scan_message(request.get_json())

    def _scan_message(self, message):
        if "content" not in message:
            return _bad_request("Body must contain 'content' attribute.")
        
        if "author" not in message:
            return _bad_request("Body must contain 'author' attribute.")
        
        if self._is_status_update_message(message):
            event = IdentifiedProjectStatusMessage(input=message["content"],
                                                   author=message["author"])
            self._emmit_event(event)
        elif self._is_message_urgent(message):
            pass
        
        return _ok()
    
    def _is_status_update_message(self, message) -> bool:
        ATTENTION_TAG = "attention"

        requirements = [
            {
                "requirement": "The message can be ignored.",
                "tag": "ignore"
            },
            {
                "requirement": "The message is not asking for a status update, it is a normal message.",
                "tag": "normal"
            },
            {
                "requirement": "The message is asking for a status update and it needs attention.",
                "tag": ATTENTION_TAG
            }
        ]

        return self._run_scan_message_chain(message, requirements, match_tag=ATTENTION_TAG)
    
    def _is_message_urgent(self, message) -> bool:
        ATTENTION_TAG = "attention"

        requirements = [
            {
                "requirement": "The message is not important and can be ignored.",
                "tag": "ignore"
            },
            {
                "requirement": "The message should not be ignored but is not urgent.",
                "tag": "normal"
            },
            {
                "requirement": "The message is important and requires immediate attention.",
                "tag": ATTENTION_TAG
            }
        ]

        return self._run_scan_message_chain(message, requirements, match_tag=ATTENTION_TAG)
    
    def _run_scan_message_chain(self, message, requirements: dict, match_tag: str) -> bool:
        if not message or "content" not in message:
            raise ValueError("Message must have 'content' attribute.")
        
        chain = hub.pull("znas/scan_message") | ChatOpenAI(model=OPEN_AI_MODEL, temperature=0)

        result = chain.invoke({
            "input": message["content"],
            "requirements": json.dumps(requirements)
        })

        if not result or "tags" not in result:
            raise ValueError("Result is missing 'tags' attribute.")
        
        return match_tag in (tag.lower() for tag in result["tags"])
    
    def _handle_event(self, event):
        super()._handle_event(event)
        
        if isinstance(event, IdentifiedUrgentMessage):
            self._handle_identified_urgent_message_event(event)
        elif isinstance(event, RespondProjectStatusMessage):
            self._handle_respond_project_status_message_event(event)
        elif isinstance(event, RespondUrgentMessage):
            self._handle_respond_urgent_message_event(event)
        else:
            logging.debug(f"Event '{type(event).__name__}' is not supported.")
    
    def _handle_identified_urgent_message_event(self, event: IdentifiedUrgentMessage):
        logging.debug(f"Handling '{type(event).__name__}'.")

        # Emmit event to respond to an urgent message.
        self.on_next(RespondUrgentMessage())

    def _handle_respond_project_status_message_event(self, event: RespondProjectStatusMessage):
        logging.debug(f"Handling '{type(event).__name__}'.")
    
    def _handle_respond_urgent_message_event(self, event: RespondUrgentMessage):
        logging.debug(f"Handling '{type(event).__name__}'.")

    def start(self):
        self.server.run(debug=True, port=5000)

def _ok(message="success"):
    return jsonify({
        "message": message
    }), 200

def _bad_request(error: str):
    return jsonify({"error": error}), 400
    