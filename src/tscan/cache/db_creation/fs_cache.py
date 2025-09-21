from tscan.cache.connection import FSCacheConnection


def create_db_fs_cache(connection: FSCacheConnection) -> int:
    with connection:
        pass
