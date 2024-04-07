class IdentifiedProjectStatusMessage:
    def __init__(self, content: dict):
        self._validate_content(content)

        self.content = content

    def _validate_content(self, content: dict):
        if not content:
            raise ValueError("Content cannot be None.")
            
        error_message = "Content is missing '{}' attribute."
        required_attrs = ["input", "_from"]
        
        for attr in required_attrs:
            if attr not in content:
                raise ValueError(error_message.format(attr))


class RespondProjectStatusMessage:
    pass