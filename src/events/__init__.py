from enum import Enum
from pydantic import BaseModel, field_validator
from helpers import ValidationHelper

class MessageEvalResult(Enum):
    IGNORE = "ignore"
    STATUS_UPDATE = "status_update"
    URGENT = "urgent"

class BaseEvent(BaseModel):
    message_content: str
    confidence: int
    eval_result: MessageEvalResult

    @field_validator("message_content")
    def check_message_content_field(cls, value: str, info):
        ValidationHelper.raise_if_str_none_or_empty(value, info)
        return value
    
    @field_validator("confidence")
    def check_confidence(cls, value: int, info):
        if value < 0 or value > 5:
            raise ValueError(f"The field '{info.field_name}' is not between 0 and 5.")
        return value
