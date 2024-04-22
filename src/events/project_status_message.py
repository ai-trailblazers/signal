from . import BaseEvent, MessageEvalResult
from pydantic import BaseModel, field_validator, model_validator
from helpers import ValidationHelper

class IdentifiedProjectStatusMessageEvent(BaseEvent):
    project: str

    @field_validator("project")
    def check_project_field(cls, value: str, info):
        ValidationHelper.raise_if_str_none_or_empty(value, info)
        return value
    
    @model_validator(mode="before")
    def check_eval_result_field(cls, values):
        values['eval_result'] = MessageEvalResult.STATUS_UPDATE
        return values

class RespondProjectStatusMessageEvent(BaseModel):
    pass