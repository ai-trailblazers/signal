from . import Event, MessageEvalResult
from pydantic import BaseModel, field_validator

class IdentifiedUrgentMessageEvent(Event):
    pass

class RespondUrgentMessageEvent(BaseModel):
    pass