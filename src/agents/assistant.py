import logging
import trio
import os

from . import Agent, RAG, Scanner, VectorDB
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field
from langchain_community.agent_toolkits import SlackToolkit
from events import Message, Event, MessageEvalResult
from events.project_status_message import IdentifiedProjectStatusMessageEvent, RespondProjectStatusMessageEvent
from events.urgent_message import IdentifiedUrgentMessageEvent, RespondUrgentMessageEvent

CONFIDENCE_THRESHOLD_STATUS_UPDATE_MESSAGE = 4
CONFIDENCE_THRESHOLD_URGENT_MESSAGE = 4
CHANNEL = "CBU1NB2P3"
MEMBER_ID = "UBUJ122AW"

class Assistant(Agent, RAG, Scanner):
    def __init__(self, vector_db: VectorDB):
        tools = SlackToolkit().get_tools()
        Agent.__init__(self, tools, legacy=False)
        RAG.__init__(self, vector_db)
        Scanner.__init__(self)
        self.slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
    
    def _check_if_status_update_message(self, message: Message) -> IdentifiedProjectStatusMessageEvent:
        model_dump = message.model_dump()
        output = self._run_chain(prompt="znas/identify_project_status_message",
                                 input=model_dump)
        event = IdentifiedProjectStatusMessageEvent(**message.model_dump(), **output)
        return event if event.confidence >= CONFIDENCE_THRESHOLD_STATUS_UPDATE_MESSAGE else None
    
    def _check_if_urgent_message(self, message: Message) -> IdentifiedUrgentMessageEvent:
        model_dump = message.model_dump()
        output = self._run_chain(prompt="znas/identify_urgent_message",
                                 input=model_dump)
        event = IdentifiedUrgentMessageEvent(**model_dump, **output)
        return event if event.confidence >= CONFIDENCE_THRESHOLD_URGENT_MESSAGE else None

    def _scan_message(self, message: Message):
        check_functions = [self._check_if_status_update_message, self._check_if_urgent_message]
        for check_function in check_functions:
            event: Event = check_function(message)
            if event:
                self._emit_event(event, is_local_event=event.eval_result is MessageEvalResult.URGENT)
                return
        logging.info(f"Ignoring message '{event.text}'")

    async def retrieve_messages_from_user_in_channel(self, channel_id: str, user_id: str):
        current_time = datetime.now(tz=timezone.utc)
        twenty_four_hours_ago = current_time - timedelta(days=1)
        response = await trio.to_thread.run_sync(
                lambda: self.slack_client.conversations_history(
                    channel=channel_id,
                    oldest=str(twenty_four_hours_ago.timestamp()),
                    inclusive=True
                )
            )
        if response.get("ok", False):
            for message in [msg for msg in response.get("messages", []) if msg.get("user") == user_id]:
                self._scan_message(Message(**message))

    async def _scan(self):
        async with trio.open_nursery() as nursery:
            nursery.start_soon(self.retrieve_messages_from_user_in_channel, CHANNEL, MEMBER_ID)
    
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

    def _handle_respond_project_status_message_event(self, event: RespondProjectStatusMessageEvent):
        pass
    
    def _handle_respond_urgent_message_event(self, event: RespondUrgentMessageEvent):
        pass

    def online(self, scanner_interval_seconds=300):
        Scanner._start(self, scanner_interval_seconds)
    