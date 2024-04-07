from abc import ABC
from typing import List

class BaseMessage(ABC):
    _REQUIRED_ATTR_INPUT="input"

    def __init__(self, content: dict, required_attrs: List[str]):
        self._validate_content(content, required_attrs)
        self.content = content
    
    def _validate_content(self, content: dict, required_attrs: List[str]):
        if not content:
            raise ValueError("Content cannot be None.")
        
        if self._REQUIRED_ATTR_INPUT not in required_attrs:
            required_attrs.append(self._REQUIRED_ATTR_INPUT)
        
        for attr in required_attrs:
            if attr not in content:
                raise ValueError("Content is missing '{}' attribute.".format(attr))

class IdentifiedProjectStatusMessage(BaseMessage):
    _REQUIRED_ATTR_FROM="_from"

    def __init__(self, content: dict):
        super().__init__(content, required_attrs=[self._REQUIRED_ATTR_FROM])


class RespondProjectStatusMessage(BaseMessage):
    _REQUIRED_ATTR_PLACEHOLDER="placeholder"

    def __init__(self, content: dict):
        super().__init__(content, required_attrs=[self._REQUIRED_ATTR_PLACEHOLDER])