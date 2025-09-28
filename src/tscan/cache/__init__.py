from typing import List, TypeAlias

from tscan.cache.model_query import _ModelQuery, ModelDictParams  # type: ignore
from tscan.cache.connection import FSCacheConnection


ModelQuery: TypeAlias = _ModelQuery
for op_name in ModelQuery.OPERATOR_MAP:
    method = ModelQuery.create_operator_method(op_name)
    decorated_method = ModelQuery.tablename_exists(method)
    setattr(ModelQuery, op_name, decorated_method)

__all__: List[str] = [
    "ModelQuery",
    "ModelDictParams",
    "FSCacheConnection",
]
