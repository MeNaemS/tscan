TYPE_ERROR_MSG: str = "{field_name} must be of type {type_name}."
NON_NEGATIVE_ERROR_MSG: str = "{field_name} must be a non-negative integer."


class ValidationError(Exception):
    def __init__(self, variable_name: str, message: str, *args, **kwargs) -> None:
        self.__variable_name: str = variable_name
        self.__message: str = message.format(*args, **kwargs)
        super().__init__(
            f"{self.__variable_name}: {self.__message}"
        )
