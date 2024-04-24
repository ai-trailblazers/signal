from . import Event, MessageEvalResult
from pydantic import BaseModel, field_validator

class IdentifiedUrgentMessageEvent(Event):
    def __init__(self, message_content, confidence):
        super().__init__(message_content, confidence, MessageEvalResult.URGENT)

class RespondUrgentMessageEvent(BaseModel):
    pass