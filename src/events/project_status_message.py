from typing import List
from . import BaseEvent, MessageEvalResult
from pydantic import BaseModel, Field, field_validator, model_validator
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

class ProjectStatusQueryItem(BaseModel):
    question: str = Field(..., description="A question intended to collect information about a project.")
    purpose: str = Field(..., description="The reason for the question to provide context.")
    answer: str = Field(default="", description="The response to the question, initially empty.")

class RespondProjectStatusMessageEvent(IdentifiedProjectStatusMessageEvent):
    dataset: List[ProjectStatusQueryItem] = Field(default_factory=list, description="A list of data queries for the project status report.")

    @field_validator('dataset')
    def validate_dataset(cls, value, info):
        if any(not isinstance(item, ProjectStatusQueryItem) for item in value):
            raise ValueError("All items in the dataset must be instances of ProjectStatusQueryItem.")
        return value
