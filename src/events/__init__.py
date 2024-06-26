from enum import Enum
from pydantic import BaseModel, Field, field_validator
from helpers import ValidationHelper

class MessageEvalResult(Enum):
    IGNORE = "ignore"
    STATUS_UPDATE = "status_update"
    URGENT = "urgent"
    
class Message(BaseModel):
    user: str = Field(...)
    type: str = Field(...)
    ts: str = Field(...)
    client_msg_id: str = Field(...)
    text: str = Field(...)

class Event(Message):
    confidence: int
    eval_result: MessageEvalResult
    
    @field_validator("confidence")
    def check_confidence(cls, value: int, info):
        if value < 0 or value > 5:
            raise ValueError(f"The field '{info.field_name}' is not between 0 and 5.")
        return value
