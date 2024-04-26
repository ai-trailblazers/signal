from . import Event, MessageEvalResult
from datetime import datetime, timezone
from pydantic import BaseModel, Field, model_validator
from langchain_core.documents import Document

class IdentifiedProjectStatusMessageEvent(Event):
    project: str = Field(default="")
    
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
    context: str = Field(...)
