from . import Event, MessageEvalResult
from pydantic import BaseModel, model_validator

class IdentifiedUrgentMessageEvent(Event):
    @model_validator(mode="before")
    def check_eval_result_field(cls, values):
        values['eval_result'] = MessageEvalResult.STATUS_UPDATE
        return values

class RespondUrgentMessageEvent(BaseModel):
    pass