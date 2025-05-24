import json
from typing import Any, Callable

class ValidationError(Exception):
    """Minimal ValidationError used for tests."""

class BaseModel:
    def __init__(self, **data: Any) -> None:
        for k, v in data.items():
            setattr(self, k, v)

    @classmethod
    def model_validate(cls, data: Any):
        if isinstance(data, cls):
            return data
        if isinstance(data, dict):
            return cls(**data)
        raise ValidationError("Invalid data")

    @classmethod
    def model_validate_json(cls, data: str):
        return cls.model_validate(json.loads(data))

    def model_dump(self) -> dict:
        return self.__dict__

    def model_dump_json(self) -> str:
        return json.dumps(self.model_dump())

class RootModel(BaseModel):
    def __init__(self, root: Any) -> None:
        self.root = root

    def __class_getitem__(cls, item: Any):
        """Ignore generics used in type hints and return the base class."""
        return cls

ConfigDict = dict

def field_serializer(*_args: Any, **_kwargs: Any) -> Callable[[Callable], Callable]:
    def decorator(fn: Callable) -> Callable:
        return fn
    return decorator

def field_validator(*_args: Any, **_kwargs: Any) -> Callable[[Callable], Callable]:
    def decorator(fn: Callable) -> Callable:
        return fn
    return decorator

def model_serializer(fn: Callable) -> Callable:
    return fn
