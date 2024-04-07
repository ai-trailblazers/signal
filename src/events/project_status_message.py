from . import BaseMessage

class IdentifiedProjectStatusMessage(BaseMessage):
    _REQUIRED_ATTR_FROM="_from"

    def __init__(self, content: dict):
        super().__init__(content, required_attrs=[self._REQUIRED_ATTR_FROM])


class RespondProjectStatusMessage(BaseMessage):
    _REQUIRED_ATTR_PLACEHOLDER="placeholder"

    def __init__(self, content: dict):
        super().__init__(content, required_attrs=[self._REQUIRED_ATTR_PLACEHOLDER])