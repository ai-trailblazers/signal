from . import BaseMessage

class IdentifiedUrgentMessage:
    _REQUIRED_ATTR_PLACEHOLDER="placeholder"

    def __init__(self, content: dict):
        super().__init__(content, required_attrs=[self._REQUIRED_ATTR_PLACEHOLDER])

class RespondUrgentMessage:
    _REQUIRED_ATTR_PLACEHOLDER="placeholder"

    def __init__(self, content: dict):
        super().__init__(content, required_attrs=[self._REQUIRED_ATTR_PLACEHOLDER])