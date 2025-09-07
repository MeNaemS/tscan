from typing import Optional, Union, overload
from os import name, getenv
from pathlib import Path


@overload
def get_cache_dir(path: None = None) -> Path:
    """
    Returns the default cache directory.
    Args:
        path: Optional, default to None.
            When None, the function will create or detect the default cache directory.
    Returns:
        Path: A Path object pointing to the default cache directory.
    """
    ...
@overload
def get_cache_dir(
    path: str,
    use_cache: bool = True,
    create_if_not_exists: bool = False,
) -> Optional[Path]:
    """
    Returns a Path object pointing to the cache directory specified by the given string path.
    Args:
        path: A string representing the path to the desired cache directory.
        use_cache: A boolean value indicating whether to use the cache directory.
        create_if_not_exists: A boolean value indicating whether to create the
            directory if it doesn't exist.
    Returns:
        Path: A Path object pointing to the cache directory specified by the input string.
    """
    ...
@overload
def get_cache_dir(
    path: Path,
    use_cache: bool = True,
    create_if_not_exists: bool = False,
) -> Optional[Path]:
    """
    Returns the input Path object pointing to the cache directory.
    Args:
        path: A path object representing the cache direcoty.
        use_cache: A boolean value indicating whether to use the cache directory.
        create_if_not_exists: A boolean value indicating whether to create the
            directory if it doesn't exist.
    Returns:
        Path: The input Path object, which points to the cache directory.
    """
    ...


def get_cache_dir(
    path: Optional[Union[str, Path]] = None,
    use_cache: bool = True,
    create_if_not_exists: bool = False,
) -> Optional[Path]:
    """
    Obtaining or creating a directory with cache.
    Args:
        path: Optional value (can be None, str, Path).
            If None, the function will create/detect the directory itself.
            If str, it will convert to Path, check for existence, and return.
            If Path, it will return.
        use_cache: Optional value (default True).
            If True, the function will use the cache directory.
        create_if_not_exists: Optional value (default False).
            If True, the function will create the directory if it doesn't exist.
    Returns:
        Path: Object pointing to the cache directory.
    """
    # If use_cache is False, caching will not be used.
    if not use_cache:
        return
    
    cache_path: Path
    # Path processing and existence check.
    if isinstance(path, Path):
        cache_path = path

    # If path is a string, convert it to a Path object and check for existence.
    elif isinstance(path, str):
        cache_path = Path(path)

    # If path is None, create a default cache directory.
    elif path is None:
        if name == "nt":  # Windows.
            cache_path = Path(getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        else:
            cache_path = Path(getenv("XDG_CACHE_HOME", Path.home() / ".cache"))
    else:
        raise TypeError(f"Invalid type for path: {type(path)}")

    # Create the cache directory if it doesn't exist.
    if not cache_path.exists():
        if create_if_not_exists:
            try:
                cache_path.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as error:
                raise RuntimeError(f"Failed to create cache directory \"{cache_path}\": {error}")
        else:
            raise FileNotFoundError(f"Cache directory \"{cache_path}\" does not exist.")

    return cache_path.resolve()
