from typing import List, Optional, Dict, Any, Tuple, TypeAlias, Callable, Literal, Iterable
from re import sub

from tscan.exc import TablenameDoesNotExist, messages


ModelTupleValues: TypeAlias = Tuple[Any, Any]
ModelListOfTuples: TypeAlias = List[ModelTupleValues]
ModelDictParams: TypeAlias = Dict[str, ModelListOfTuples]


class ModelQuery:
    __slots__: Tuple[str, ...] = (
        "__query",
        "__params",
        "__values",
        "__set",
        "__join",
        "__order_by",
        "__pagination",
        "__returning"
    )
    # Mapping of operator name to operator symbol
    _OPERATOR_MAP: Dict[str, str] = {
        "equal": "=",
        "not_equal": "<>",
        "greater_than": ">",
        "less_than": "<",
        "greater_than_or_equal": ">=",
        "less_than_or_equal": "<=",
        "like": "LIKE",
        "not_like": "NOT LIKE",
        "in_": "IN",
        "not_in": "NOT IN",
        "is_null": "IS NULL",
        "is_not_null": "IS NOT NULL",
    }

    def __init__(
        self,
        *,
        query: Optional[str] = None,
        params: Optional[ModelDictParams] = None,
        values: Optional[Dict[str, Any]] = None,
        set_values: Optional[Dict[str, Any]] = None,
        join: Optional[List[Tuple[str, str]]] = None,
        order_by: Optional[List[Tuple[str, str]]] = None,
        pagination: Optional[Tuple[Optional[int], Optional[int]]] = None,
        returning: Optional[List[str]] = None
    ) -> None:
        self.__query: Optional[str] = query

        self.__params: ModelDictParams
        if params is None:
            self.__params = self.__generate_base_params()
        else:
            self.__params = params
        
        self.__values: Optional[Dict[str, Any]] = values
        self.__set: Optional[Dict[str, Any]] = set_values
        self.__join: Optional[List[Tuple[str, str]]] = join
        self.__order_by: Optional[List[Tuple[str, str]]] = order_by
        self.__pagination: Optional[Tuple[Optional[int], Optional[int]]] = pagination
        self.__returning: Optional[List[str]] = returning

    def __clone_with(
        self,
        *,
        query: Optional[str] = None,
        params: Optional[ModelDictParams] = None,
        values: Optional[Dict[str, Any]] = None,
        set_values: Optional[Dict[str, Any]] = None,
        join: Optional[List[Tuple[str, str]]] = None,
        order_by: Optional[List[Tuple[str, str]]] = None,
        pagination: Optional[Tuple[Optional[int], Optional[int]]] = None,
        returning: Optional[List[str]] = None
    ) -> "ModelQuery":
        return self.__class__(
            query=query if query is not None else self.__query,
            params=params if params is not None else self.__params,
            values=values if values is not None else self.__values,
            set_values=set_values if set_values is not None else self.__set,
            join=join if join is not None else self.__join,
            order_by=order_by if order_by is not None else self.__order_by,
            pagination=pagination if pagination is not None else self.__pagination,
            returning=returning if returning is not None else self.__returning
        )

    @staticmethod
    def __requires_tablename(func: Callable[..., "ModelQuery"]) -> Callable[..., "ModelQuery"]:
        def wrapper(self: "ModelQuery", *args: Any, **kwargs: Any) -> "ModelQuery":
            if self.__query is None:
                raise TablenameDoesNotExist(messages.TABLENAMEDOESNOTEXIST_ERROR_MSG, self)
            return func(self, *args, **kwargs)
        
        return wrapper

    @staticmethod
    def _tablename_exists(
        func: Callable[["ModelQuery", str, Any], "ModelQuery"]
    ) -> Callable[["ModelQuery", str, Any], "ModelQuery"]:
        def wrapper(self: "ModelQuery", column: str, value: Any) -> "ModelQuery":
            if self.__query is None:
                raise TablenameDoesNotExist(messages.TABLENAMEDOESNOTEXIST_ERROR_MSG, self)
            return func(self, column, value)
        
        return wrapper

    @staticmethod
    def _create_operator_method(
        op_name: str
    ) -> Callable[["ModelQuery", str, Any], "ModelQuery"]:
        def method(self: "ModelQuery", column: str, value: Any) -> "ModelQuery":
            if op_name not in self._OPERATOR_MAP:
                raise NotImplementedError(
                    "The operator '{op_name}' is not supported.".format(op_name=op_name)
                )
            new_params: ModelDictParams = self.__params.copy()
            new_params[op_name].append((column, value))
            return self.__clone_with(params=new_params)

        method.__name__ = op_name
        method.__doc__ = "Add the '{op_name}' operator to the query.".format(
            op_name=op_name
        )

        return method

    @property
    def query_data(self) -> Optional[str]:
        return self.__query

    @property
    def params_data(self) -> Optional[ModelDictParams]:
        return self.__params

    @property
    def values_data(self) -> Optional[Dict[str, Any]]:
        return self.__values

    @property
    def set_values_data(self) -> Optional[Dict[str, Any]]:
        return self.__set

    @property
    def join_data(self) -> Optional[List[Tuple[str, str]]]:
        return self.__join

    @property
    def order_by_data(self) -> Optional[List[Tuple[str, str]]]:
        return self.__order_by

    @property
    def pagination_data(self) -> Optional[Tuple[Optional[int], Optional[int]]]:
        return self.__pagination

    @property
    def limit_data(self) -> Optional[int]:
        return None if self.__pagination is None else self.__pagination[1]

    @property
    def offset_data(self) -> Optional[int]:
        return None if self.__pagination is None else self.__pagination[0]

    @property
    def returning_data(self) -> Optional[List[str]]:
        return self.__returning

    def __generate_base_params(self) -> ModelDictParams:
        """Generate the base parameters for the query."""
        return {key: [] for key in self._OPERATOR_MAP.keys()}

    def select(self, tablename: str, columns: Optional[List[str]] = None) -> "ModelQuery":
        """Select the columns from the table."""
        resulted_columns: str = "*" if not columns else ",".join(columns)
        return self.__clone_with(
            query="SELECT {columns} FROM {tablename}".format(
                columns=resulted_columns,
                tablename=tablename
            )
        )

    @__requires_tablename
    def where(self, *args: List["ModelQuery"]) -> "ModelQuery":
        if not args:
            return self

        new_params: ModelDictParams = self.__params.copy()
        for arg in args:
            new_params |= arg.params
            
        return self.__clone_with(params=new_params)

    def insert(self, tablename: str) -> "ModelQuery":
        return self.__clone_with(query="INSERT INTO {tablename}".format(tablename=tablename))

    @__requires_tablename
    def values(self, **kwargs: Dict[str, Any]) -> "ModelQuery":
        if not kwargs:
            return self
        
        new_values: Dict[str, Any] = self.__values.copy() if self.__values else {}
        new_values.update(kwargs)
        return self.__clone_with(values=new_values)

    def delete(self, tablename: str) -> "ModelQuery":
        return self.__clone_with(query="DELETE FROM {tablename}".format(tablename=tablename))

    def update(self, tablename: str) -> "ModelQuery":
        return self.__clone_with(query="UPDATE {tablename}".format(tablename=tablename))

    @__requires_tablename
    def set(self, **kwargs: Dict[str, Any]) -> "ModelQuery":
        if not kwargs:
            return self
        
        new_set: Dict[str, Any] = self.__set.copy() if self.__set else {}
        new_set.update(kwargs)
        return self.__clone_with(set_values=new_set)

    @__requires_tablename
    def join(self, tablename: str, condition: str) -> "ModelQuery":
        join: List[Tuple[str, str]] = [] if self.__join is None else self.__join.copy()
        join.append((tablename, condition))
        return self.__clone_with(join=join)

    @__requires_tablename
    def order_by(self, column: str, order_type: Literal["ASC", "DESC"] = "ASC") -> "ModelQuery":
        order_by: List[Tuple[str, str]] = [] if self.__order_by is None else self.__order_by.copy()
        order_by.append((column, order_type))
        return self.__clone_with(order_by=order_by)

    @__requires_tablename
    def limit(self, limit: int) -> "ModelQuery":
        if limit < 0:
            raise ValueError("Limit must be a positive integer.")

        return self.__clone_with(
            pagination=(None if self.__pagination is None else self.__pagination[0], limit)
        )
    
    @__requires_tablename
    def offset(self, offset: int) -> "ModelQuery":
        if offset < 0:
            raise ValueError("Offset must be a positive integer.")

        return self.__clone_with(
            pagination=(offset, None if self.__pagination is None else self.__pagination[1])
        )

    @__requires_tablename
    def returning(self, *args: List[str]) -> "ModelQuery":
        if not args:
            return self
        
        returning: List[str] = [] if self.__returning is None else self.__returning.copy()
        returning += args
        return self.__clone_with(returning=returning)

    def build(self) -> Tuple[str, List[Any]]:
        """
        Build the SQL query and parameters.

        ### Returns:
            ```Tuple[str, List[Any]]: The SQL query and parameters.
        """
        if self.__query is None:
            raise TablenameDoesNotExist(messages.TABLENAMEDOESNOTEXIST_ERROR_MSG, self)
        
        sql: str = self.__query
        params: List[Any] = []

        # Join
        if self.__join and self.__query.startswith("SELECT"):
            for tablename, condition in self.__join:
                sql += f" JOIN {tablename} ON {condition}"

        # Set (UPDATE)
        if self.__set and self.__query.startswith("UPDATE"):
            set_clauses: List[str] = []
            for column, value in self.__set.items():
                set_clauses.append(f"{column} = ?")
                params.append(value)
            sql += " SET " + ", ".join(set_clauses)
        
        # Values (INSERT)
        if self.__values and self.__query.startswith("INSERT"):
            columns: str = ", ".join(self.__values.keys())
            placeholders: str = ", ".join(["?"] * len(self.__values))
            sql += f" ({columns}) VALUES ({placeholders})"
            params.extend(self.__values.values())

        # Where
        if any(self.__params.values()):
            where_clauses: List[str] = []
            for op_name, conditions in self.__params.items():
                if not conditions:
                    continue
                op_symbol: str = self._OPERATOR_MAP[op_name]
                for column, value in conditions:
                    if op_name in ("is_null", "is_not_null"):
                        where_clauses.append(f"{column} {op_symbol}")
                    elif op_name in ("in", "not_in"):
                        if not isinstance(value, (list, tuple)):
                            raise ValueError(
                                "The 'in' and 'not_in' operators require a list or tuple."
                            )
                        placeholders: str = ", ".join(["?"] * len(value))
                        where_clauses.append(f"{column} {op_symbol} ({placeholders})")
                        params.extend(value)
                    else:
                        where_clauses.append(f"{column} {op_symbol} ?")
                        params.append(value)
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)

        # Order by
        if self.__order_by and self.__query.startswith("SELECT"):
            order_parts: List[str] = [f"{col} {direction}" for col, direction in self.__order_by]
            sql += " ORDER BY " + ", ".join(order_parts)

        # LIMIT / OFFSET
        if self.__pagination and self.__query.startswith("SELECT"):
            offset, limit = self.__pagination
            if limit is not None:
                sql += f" LIMIT {limit}"
            if offset is not None:
                sql += f" OFFSET {offset}"

        # Returning
        if self.__returning and (
            self.__query.startswith("INSERT") or self.__query.startswith("UPDATE")
        ):
            returning_cols: str = ", ".join(self.__returning)
            sql += f" RETURNING {returning_cols}"
        
        return sql, params

    def preview(self) -> str:
        """
        Preview the SQL query.\n
        Note: This method does not build the query.

        ### Returns:
            ```str: The previewed SQL query.
        """
        try:
            sql, params = self.build()
            param_iter: Iterable = iter(params)

            def replacer(match: str) -> str:
                try:
                    val: Any = next(param_iter)
                    if val is None:
                        return "NULL"
                    elif isinstance(val, str):
                        return f"'{val.replace("'", "''")}'"
                    elif isinstance(val, (int, float)):
                        return str(val)
                    else:
                        return repr(val)
                except StopIteration:
                    return "?"
            
            sql: str = sub(r"\?", replacer, sql)
            return sql

        except Exception as error:
            return f"/* PREVIEW ERROR: {type(error).__name__}: {error} */"


    def __repr__(self) -> str:
        return (
            f"ModelQuery(query={self.__query!r}, params={self.__params}, "
            f"values={self.__values}, set_values={self.__set}, order_by={self.__order_by}, "
            f"join={self.__join}, "
            f"limit={None if self.__pagination is None else self.__pagination[1]}, "
            f"offset={None if self.__pagination is None else self.__pagination[0]}, "
            f"returning={self.__returning})"
        )

    def __str__(self) -> str:
        return self.__repr__()


for op_name in ModelQuery._OPERATOR_MAP:
    method = ModelQuery._create_operator_method(op_name)
    decorated_method = ModelQuery._tablename_exists(method)
    setattr(ModelQuery, op_name, decorated_method)
