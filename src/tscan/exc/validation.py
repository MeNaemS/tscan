from typing import Any


class ValidationError(Exception):
    def __init__(self, variable_name: str, message: str, *args: Any, **kwargs: Any) -> None:
        self.__variable_name: str = variable_name
        self.__message: str = message.format(*args, **kwargs)
        super().__init__(
            f"{self.__variable_name}: {self.__message}"
        )
