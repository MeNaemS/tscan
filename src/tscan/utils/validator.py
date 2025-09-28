from typing import (
    Any, Type, TypeVar, get_origin, get_args, Optional, Union, Tuple, List
)

from tscan.exc import ValidationError


T = TypeVar("T")


class ValidateObject:
    @classmethod
    def validate_object(
        cls,
        obj: Any, variable_name: str, required_type: Type[T],
        message: str, *args: Any, **kwargs: Any
    ) -> T:
        if not cls.__isinstance(obj, required_type):
            raise ValidationError(variable_name, message, *args, **kwargs)
        return obj

    @classmethod
    def __check_list(cls, items: List[Any], item_type: Type[Any]) -> bool:
        for item in items:
            if not cls.__isinstance(item, item_type):
                return False
        return True

    @classmethod
    def __isinstance(cls, obj: Any, required_type: Type[T]) -> bool:
        # If required type is Union or Optional, check if obj is any of the types in the union
        origin: Optional[Any] = get_origin(required_type)

        # If required type is Any, return True to allow any type
        if origin is Any:
            return True

        if origin is Union:
            args = get_args(required_type)
            if None in args or type(None) in args:
                return any(cls.__isinstance(obj, arg) for arg in args if arg is not type(None))
            return any(cls.__isinstance(obj, arg) for arg in get_args(required_type))

        # If required type is List, check if obj is a list and all items are of the same type
        elif origin is list:
            if not isinstance(obj, list):
                return False
            item_type: Type[Any] = get_args(required_type)[0]
            return cls.__check_list(obj, item_type)  # type: ignore

        # If required type is Tuple, check if obj is a tuple and all items are of the same type
        elif origin is tuple:
            if not isinstance(obj, tuple):
                return False
            tuple_args: Tuple[Type[Any], ...] = get_args(required_type)
            if not tuple_args:
                return True
            if tuple_args[-1] is ...:  # type: ignore
                tuple_item_type: Type[Any] = tuple_args[0]
                return all(cls.__isinstance(item, tuple_item_type) for item in obj)  # type: ignore
            if len(tuple_args) != len(obj):  # type: ignore
                return False
            return all(cls.__isinstance(item, arg) for item, arg in zip(obj, tuple_args))  # type: ignore
        
        # If required type is Dict, check if obj is a dict and all keys and values are of the same type
        elif origin is dict:
            if not isinstance(obj, dict):
                return False
            key_type, val_type = get_args(required_type)
            return all(
                cls.__isinstance(key, key_type) and cls.__isinstance(val, val_type)
                    for key, val in obj.items()  # type: ignore
            )
        
        # Another type
        return isinstance(obj, required_type)

    @classmethod
    def validate_int(
        cls,
        obj: int, variable_name: str, message: str, *args: Any, **kwargs: Any
    ) -> int:
        return cls.validate_object(obj, variable_name, int, message, *args, **kwargs)

    @classmethod
    def validate_int_non_negative(
        cls,
        obj: int, variable_name: str, message: str, *args: Any, **kwargs: Any
    ) -> int:
        cls.validate_object(obj, variable_name, int, message, *args, **kwargs)
        if obj < 0:
            raise ValidationError(variable_name, message, *args, **kwargs)
        return obj

    @classmethod
    def validate_int_not_zero(
        cls,
        obj: int, variable_name: str, message: str, *args: Any, **kwargs: Any
    ) -> int:
        validated_obj = cls.validate_object(obj, variable_name, int, message, *args, **kwargs)
        if validated_obj == 0:
            raise ValidationError(variable_name, message, *args, **kwargs)
        return validated_obj

    @classmethod
    def validate_bool(
        cls,
        obj: bool, variable_name: str, message: str, *args: Any, **kwargs: Any
    ) -> bool:
        return cls.validate_object(obj, variable_name, bool, message, *args, **kwargs)
