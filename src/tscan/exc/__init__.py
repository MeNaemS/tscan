from typing import List
from types import ModuleType
from sys import modules

from tscan.exc.validation import ValidationError
from tscan.exc.database import TablenameDoesNotExist


# Create a fake module and add constants to it.
__messages_module = ModuleType("tscan.exc.messages")
__messages_module.__dict__["TYPE_ERROR_MSG"] = "{field_name} must be of type {type_name}."
__messages_module.__dict__["NON_NEGATIVE_ERROR_MSG"] = "{field_name} must be a non-negative integer."
__messages_module.__dict__["NON_ZERO_ERROR_MSG"] = "{field_name} must be a non-zero integer."
__messages_module.__dict__["TABLENAMEDOESNOTEXIST_ERROR_MSG"] = (
    "The query ({repr_query}) does not specify the table name."
)

# Add the fake module to sys.modules
modules["tscan.exc.messages"] = __messages_module

messages = __messages_module

__all__: List[str] = [
    "ValidationError",
    "TablenameDoesNotExist",
    "messages"
]
