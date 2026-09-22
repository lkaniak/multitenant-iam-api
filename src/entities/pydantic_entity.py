from pydantic import BaseModel


class BaseModelDefault(BaseModel):
    """
    - enable bracket usage (e.g. user['name'])
    """

    def __getitem__(self, key):
        return self.model_dump()[key]

    def recreate(self, data=dict):
        return self.__class__(**data)


class BaseModelExtended(BaseModelDefault):
    """
    - Removes None properties from BaseModel when serializing
    """

    def __init__(self, **data):
        for field, value in data.items():
            if isinstance(value, (dict, str)) and not value:
                data[field] = None
        super().__init__(**data)

    def dict(self, **kwargs):
        kwargs.setdefault("exclude_none", True)
        kwargs.setdefault("exclude_unset", True)
        return super().dict(**kwargs)

    def model_dump(self, **kwargs):
        kwargs.setdefault("exclude_none", True)
        kwargs.setdefault("exclude_unset", True)
        return super().model_dump(**kwargs)

    def json(self, **kwargs):
        kwargs.setdefault("exclude_none", True)
        kwargs.setdefault("exclude_unset", True)
        return super().json(**kwargs)

    def model_dump_json(self, **kwargs):
        kwargs.setdefault("exclude_none", True)
        kwargs.setdefault("exclude_unset", True)
        return super().model_dump_json(**kwargs)
