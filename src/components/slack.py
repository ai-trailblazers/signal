import logging

from . import Agent, OPEN_AI_MODEL
from enum import Enum
from flask import Flask, request, jsonify
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import SlackToolkit
from events.project_status_message import IdentifiedProjectStatusMessage, RespondProjectStatusMessage
from events.urgent_message import IdentifiedUrgentMessage, RespondUrgentMessage

class EvalResult(Enum):
    IGNORE = "ignore"
    STATUS_UPDATE = "status_update"
    URGENT = "urgent"


class Slack(Agent):
    def __init__(self):
        self.server = Flask(__name__)
        self._configure_routes()

        super().__init__(legacy=False, tools=SlackToolkit().get_tools())

    def _configure_routes(self):
        self.server.add_url_rule("/slack/events", self._handle_slack_web_hook_event.__name__, self._handle_slack_web_hook_event, methods=["POST"])
    
    def _handle_slack_web_hook_event(self):
        if not request.is_json:
            return _bad_request("Request must contain JSON data.")
        
        return self._scan_message(request.get_json())

    def _scan_message(self, message):
        if "content" not in message or not message["content"].strip():
            return _bad_request("Body must contain 'content' attribute.")
        
        if "author" not in message or not message["author"].strip():
            return _bad_request("Body must contain 'author' attribute.")
        
        result = EvalResult.IGNORE

        if self._is_status_update_message(message):
            event = IdentifiedProjectStatusMessage(input=message["content"],
                                                   author=message["author"])
            result = EvalResult.STATUS_UPDATE
            self._emit_event(event)
        elif self._is_message_urgent(message):
            event = IdentifiedUrgentMessage(input=message["content"],
                                            author=message["author"])
            result = EvalResult.URGENT
            self._emit_event(event, is_local_event=True)
        else:
            logging.debug(f"Ignoring message")
        
        return _accepted(result)
    
    def _is_status_update_message(self, message) -> bool:
        return self._run_chain(message, prompt="znas/identify_project_status_message") >= 4
    
    def _is_message_urgent(self, message) -> bool:
        return self._run_chain(message, prompt="znas/identify_urgent_message") >= 4
    
    def _run_chain(self, message, prompt: str) -> int:
        if not message or "content" not in message:
            raise ValueError("Message must have 'content' attribute.")
        
        chain = hub.pull(prompt) | ChatOpenAI(model=OPEN_AI_MODEL, temperature=0)

        result = chain.invoke({"input": message["content"]})

        if not result or "output" not in result:
            raise ValueError("Invalid result.")
        
        return result["output"]
    
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
        result = self._invoke_prompt(prompt="hwchase17/openai-tools-agent",
                                     input={"input": "please send a message saying Hi to the #general channel"})
        logging.info(f"got something {len(result)}")

    def _handle_respond_project_status_message_event(self, event: RespondProjectStatusMessage):
        pass
    
    def _handle_respond_urgent_message_event(self, event: RespondUrgentMessage):
        pass

    def start(self):
        self.server.run(debug=True, port=5000)

def _accepted(result: EvalResult, message="accepted"):
    return jsonify({
        "result": result.value,
        "message": message
    }), 202

def _bad_request(error: str):
    return jsonify({"error": error}), 400
    