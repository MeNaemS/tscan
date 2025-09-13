from typing import Tuple, get_type_hints, Dict, ClassVar, Type
from pathlib import Path
from dataclasses import dataclass, field, fields

from tscan.utils import get_cache_dir, ValidateObject
from tscan.exc.messages import TYPE_ERROR_MSG, NON_NEGATIVE_ERROR_MSG


BASE_CACHE_DIR: Path = get_cache_dir()
CACHE_FILE: Path = BASE_CACHE_DIR / "tscan_cache.sqlite3"

DEFAULT_CACHE_TTL: int = 300
CACHE_ENABLED: bool = True
CACHE_MAX_SIZE_MB: int = 500
CACHE_USE_COMPRESSION: bool = False

ENABLE_RICH_FORMATTING: bool = True
DEFAULT_MAX_DEPTH: int = 10
IGNORE_HIDDEN: bool = False
IGNORE_PATTERNS: Tuple[str, ...] = ()
SHOW_SIZES: bool = True
USE_UNICODE_TREE: bool = True

FOLLOW_SYMLINKS: bool = False
MAX_FILE_COUNT: int = 0

PRE_SCAN_HOOK: str = ""


@dataclass(slots=True, frozen=True)
class BaseConfig:
    def __post_init__(self) -> None:
        type_hints: Dict[str, type] = get_type_hints(self)
        for dataclass_field in fields(self):
            value = getattr(self, dataclass_field.name)
            ValidateObject.validate_object(
                value,
                dataclass_field.name,
                type_hints[dataclass_field.name],
                TYPE_ERROR_MSG,
                field_name=f"{self.__class__.__name__}.{dataclass_field.name}",
                type_name=type_hints[dataclass_field.name],
            )


@dataclass(slots=True, frozen=True)
class ConfigContainer:
    def __post_init__(self) -> None:
        type_hints: Dict[str, Type[BaseConfig]] = get_type_hints(self)
        for dataclass_field in fields(self):
            value: BaseConfig = getattr(self, dataclass_field.name)
            ValidateObject.validate_object(
                value,
                dataclass_field.name,
                type_hints[dataclass_field.name],
                TYPE_ERROR_MSG,
                field_name=f"{self.__class__.__name__}.{dataclass_field.name}",
                type_name=type_hints[dataclass_field.name],
            )
            value.__post_init__()


@dataclass(slots=True, frozen=True)
class CacheConfig(BaseConfig):
    ttl: int = DEFAULT_CACHE_TTL
    enabled: bool = CACHE_ENABLED
    max_size_mb: int = CACHE_MAX_SIZE_MB
    use_compression: bool = CACHE_USE_COMPRESSION

    _non_negative_fields: ClassVar[Tuple[str, ...]] = ("ttl", "max_size_mb")

    def __post_init__(self) -> None:
        super().__post_init__()
        for field_name in self._non_negative_fields:
            value = getattr(self, field_name)
            ValidateObject.validate_int_non_negative(
                obj=value,
                variable_name=field_name,
                message=NON_NEGATIVE_ERROR_MSG,
                field_name=f"{self.__class__.__name__}.{field_name}",
            )


@dataclass(slots=True, frozen=True)
class DisplayConfig(BaseConfig):
    max_depth: int = DEFAULT_MAX_DEPTH
    enable_rich_formatting: bool = ENABLE_RICH_FORMATTING
    ignore_hidden: bool = IGNORE_HIDDEN
    ignore_patterns: Tuple[str, ...] = field(default_factory=lambda: tuple(IGNORE_PATTERNS))
    show_sizes: bool = SHOW_SIZES
    use_unicode_tree: bool = USE_UNICODE_TREE

    _non_negative_fields: ClassVar[Tuple[str, ...]] = ("max_depth",)

    def __post_init__(self) -> None:
        super().__post_init__()
        for field_name in self._non_negative_fields:
            value = getattr(self, field_name)
            ValidateObject.validate_int_non_negative(
                obj=value,
                variable_name=field_name,
                message=NON_NEGATIVE_ERROR_MSG,
                field_name=f"{self.__class__.__name__}.{field_name}",
            )


@dataclass(slots=True, frozen=True)
class SafetyConfig(BaseConfig):
    follow_symlinks: bool = FOLLOW_SYMLINKS
    max_file_count: int = MAX_FILE_COUNT
    pre_scan_hook: str = PRE_SCAN_HOOK

    _non_negative_fields: ClassVar[Tuple[str, ...]] = ("max_file_count",)

    def __post_init__(self) -> None:
        super().__post_init__()
        for field_name in self._non_negative_fields:
            value = getattr(self, field_name)
            ValidateObject.validate_int_non_negative(
                obj=value,
                variable_name=field_name,
                message=NON_NEGATIVE_ERROR_MSG,
                field_name=f"{self.__class__.__name__}.{field_name}",
            )


@dataclass(slots=True, frozen=True)
class RunTimeConfig(ConfigContainer):
    cache: CacheConfig = field(default_factory=CacheConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)


RUNTIME_CONFIG: RunTimeConfig = RunTimeConfig()
