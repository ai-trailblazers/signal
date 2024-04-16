from pydantic import BaseModel, field_validator

class BaseMessage(BaseModel):
    input: str
    author: str

    @field_validator('*')
    def check_fields(cls, value, field):
        if value is None:
            raise ValueError(f"The field '{field}' is required")
        return value
