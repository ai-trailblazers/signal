import logging
import json

from . import Agent
from flask import Flask, request, jsonify
from langchain import hub
from langchain.agents import AgentType, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from events.project_status_message import RespondProjectStatusMessage
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
        if 'content' not in message:
            return _bad_request("Body must contain 'content' attribute.")
        
        if 'author' not in message:
            return _bad_request("Body must contain 'author' attribute.")
        
        if self._is_message_urgent(message):
            logging.info("message is urgent")
        else:
            logging.info("message is not urgent")
        
        return _ok()
    
    def _is_message_urgent(self, message) -> bool:
        URGENT_TAG = "urgent"

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
                "tag": URGENT_TAG
            }
        ]
        
        chain = hub.pull("znas/scan_message") | ChatOpenAI(model="gpt-4", temperature=0)
        result = chain.invoke({
            "input": message["content"],
            "requirements": json.dumps(requirements)
        })
        
        if not result or "tags" not in result:
            raise ValueError("Result is incomplete or missing tags.")

        return URGENT_TAG in (tag.lower() for tag in result["tags"])
    
    def _handle_event(self, event):
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
    