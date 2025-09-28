from __future__ import annotations
from tscan.cache import ModelQuery


class TablenameDoesNotExist(Exception):
    def __init__(self, message: str, model_query: ModelQuery) -> None:
        super().__init__(message.format(repr_query=repr(model_query)))
