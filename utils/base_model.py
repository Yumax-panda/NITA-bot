from datetime import datetime
from typing import Any, TypeVar, get_args, get_origin, get_type_hints

T = TypeVar("T", bound="BaseModel")


class BaseModel:
    __slots__ = ()

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        type_hints = get_type_hints(cls)
        init_kwargs = {}

        for key, field_type in type_hints.items():
            value = data.get(key)

            if value is None:
                init_kwargs[key] = None
                continue

            origin = get_origin(field_type)

            # List[T]
            if origin is list:
                elem_type = get_args(field_type)[0]
                init_kwargs[key] = [cls._parse_value(elem_type, v) for v in value]

            # Dict[K, V]
            elif origin is dict:
                key_type, val_type = get_args(field_type)
                init_kwargs[key] = {
                    cls._parse_value(key_type, k): cls._parse_value(val_type, v)
                    for k, v in value.items()
                }

            else:
                init_kwargs[key] = cls._parse_value(field_type, value)

        return cls(**init_kwargs)

    @staticmethod
    def _parse_value(field_type: type, value: Any) -> Any:
        origin = get_origin(field_type)

        if origin is not None:
            # Nested generics (already handled in from_dict)
            return value

        # datetime
        if issubclass(field_type, datetime):
            return datetime.fromisoformat(value)

        # str, int, float, bool
        if issubclass(field_type, str | int | float | bool):
            return field_type(value)

        # Nested custom class
        if hasattr(field_type, "from_dict") and callable(field_type.from_dict):
            return field_type.from_dict(value)

        # fallback
        return value
