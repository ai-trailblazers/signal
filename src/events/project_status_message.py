from . import Event, MessageEvalResult
from datetime import datetime, timezone
from typing import List
from pydantic import BaseModel, Field, field_validator, model_validator
from helpers import ValidationHelper
from langchain_core.documents import Document

class IdentifiedProjectStatusMessageEvent(Event):
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

    def to_document(self) -> Document:
        content = f"Question: {self.question}\nPurpose: {self.purpose}\nAnswer: {self.answer}"
        metadata = {'timestamp': datetime.now(timezone.utc)}
        return Document(page_content=content, metadata=metadata)

class RespondProjectStatusMessageEvent(IdentifiedProjectStatusMessageEvent):
    dataset: List[ProjectStatusQueryItem] = Field(default_factory=list, description="A list of data queries for the project status report.")

    @field_validator('dataset')
    def validate_dataset(cls, value: List[ProjectStatusQueryItem], info):
        if any(not isinstance(item, ProjectStatusQueryItem) for item in value):
            raise ValueError("All items in the dataset must be instances of ProjectStatusQueryItem.")
        if any(ValidationHelper.is_str_none_or_empty(item.answer) for item in value):
            raise ValueError("All items in the dataset must have an answer.")
        return value
    
    def generate_context(self) -> str:
        context_lines = [
            "## CONTEXT ##",
            *(
                f"Question: {item.question}\nPurpose: {item.purpose}\nAnswer: {item.answer}"
                for item in self.dataset
            ),
            "#############"
        ]
        return "\n".join(context_lines)
            
