class ValidationHelper:
    @staticmethod
    def raise_if_str_none_or_empty(value: str, info):
        if value is None or value.strip() == "":
            raise ValueError(f"The field '{info.field_name}' cannot be None, empty or whitespace.")