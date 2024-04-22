import logging

from . import Agent
from flask import Flask, request, jsonify
from langchain_community.agent_toolkits import SlackToolkit
from pydantic import BaseModel, field_validator
from events import BaseEvent, MessageEvalResult
from events.project_status_message import IdentifiedProjectStatusMessageEvent, RespondProjectStatusMessageEvent
from events.urgent_message import IdentifiedUrgentMessageEvent, RespondUrgentMessageEvent
from helpers import ValidationHelper

CONFIDENCE_THRESHOLD_STATUS_UPDATE_MESSAGE = 4
CONFIDENCE_THRESHOLD_URGENT_MESSAGE = 4

class SlackMessage(BaseModel):
    content: str
    author: str
    
    @field_validator('content', 'author')
    def check_str_fields(cls, value: str, info):
        ValidationHelper.raise_if_str_none_or_empty(value, info)
        return value

class Slack(Agent):
    def __init__(self):
        tools = SlackToolkit().get_tools()
        super().__init__(tools, legacy=False)
        self.server = Flask(__name__)
        self._configure_routes()

    def _configure_routes(self):
        self.server.add_url_rule("/slack/events", self._handle_slack_web_hook_event.__name__, self._handle_slack_web_hook_event, methods=["POST"])
    
    def _handle_slack_web_hook_event(self):
        if not request.is_json:
            return _bad_request("Request must contain JSON data.")
        json = request.get_json()
        try:
            message = SlackMessage(**json)
            return self._scan_message(message)
        except ValueError as e:
            return _bad_request(str(e))
        except Exception as e:
            return _internal_server_error(str(e))

    def _scan_message(self, message: SlackMessage):
        def emit(event: BaseEvent) -> bool:
            if not event:
                return False
            self._emit_event(event, is_local_event=event.eval_result is MessageEvalResult.URGENT)
            return True
        check_functions = [self._check_if_status_update_message, self._check_if_urgent_message]
        for check_function in check_functions:
            event = check_function(message)
            if emit(event):
                return _accepted(event.eval_result)
        return _accepted(MessageEvalResult.IGNORE)
    
    def _check_if_status_update_message(self, message: SlackMessage) -> IdentifiedProjectStatusMessageEvent:
        output = self._run_chain(prompt="znas/identify_project_status_message",
                                 input={"message_content": message.content})
        event = IdentifiedProjectStatusMessageEvent(message_content=message.content, **output)
        return event if event.confidence >= CONFIDENCE_THRESHOLD_STATUS_UPDATE_MESSAGE else None
    
    def _check_if_urgent_message(self, message: SlackMessage) -> IdentifiedUrgentMessageEvent:
        output = self._run_chain(prompt="znas/identify_urgent_message",
                                 input={"input": message.content})
        event = IdentifiedUrgentMessageEvent(message_content=message.content, **output)
        return event if event.confidence >= CONFIDENCE_THRESHOLD_URGENT_MESSAGE else None
    
    def _handle_event(self, event):
        super()._handle_event(event)

        if isinstance(event, IdentifiedUrgentMessageEvent):
            self._handle_identified_urgent_message_event(event)
        elif isinstance(event, RespondProjectStatusMessageEvent):
            self._handle_respond_project_status_message_event(event)
        elif isinstance(event, RespondUrgentMessageEvent):
            self._handle_respond_urgent_message_event(event)
        else:
            logging.debug(f"Event '{type(event).__name__}' is not supported.")
    
    def _handle_identified_urgent_message_event(self, event: IdentifiedUrgentMessageEvent):
        result = self._invoke_prompt(prompt="hwchase17/openai-tools-agent",
                                     input={"input": "can you send the lyrics of the Billy Jean song from Michael Jackson to the #borderlands channel"})
        logging.info(f"got something {len(result)}")

    def _handle_respond_project_status_message_event(self, event: RespondProjectStatusMessageEvent):
        pass
    
    def _handle_respond_urgent_message_event(self, event: RespondUrgentMessageEvent):
        pass

    def start(self):
        self.server.run(debug=True, port=5000)

def _accepted(result: MessageEvalResult, message="accepted"):
    return jsonify({
        "result": result.value,
        "message": message
    }), 202

def _bad_request(error):
    return jsonify({"error": error}), 400

def _internal_server_error(error):
    return jsonify({"error": error}), 500
    