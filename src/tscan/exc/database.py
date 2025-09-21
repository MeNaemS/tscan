from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tscan.cache.model_query import ModelQuery


class TablenameDoesNotExist(Exception):
    def __init__(self, message: str, model_query: "ModelQuery") -> None:
        super().__init__(message.format(repr_query=model_query.__repr__()))
