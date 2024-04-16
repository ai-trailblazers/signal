from pydantic import BaseModel, ValidationError, validator

class BaseMessage(BaseModel):
    _input: str
    _from: str

    @validator('*', pre=True)
    def check_fields(cls, value, field):
        if value is None:
            raise ValidationError(f"{field.name} is required")
        return value
    