class ValidationHelper:
    @staticmethod
    def is_str_none_or_empty(value: str) -> bool:
        return value is None or value.strip() == ""
        
    @staticmethod
    def raise_if_str_none_or_empty(value: str, info):
        if ValidationHelper.is_str_none_or_empty(value):
            raise ValueError(f"The field '{info.field_name}' cannot be None, empty or whitespace.")