from typing import Optional, Type, TYPE_CHECKING
from sys import platform

from sqlite3 import Connection, Cursor, connect
from logging import Logger, getLogger

if TYPE_CHECKING:
    from types import TracebackType


logger: Logger = getLogger("tscan.cache.connection")


class FSCacheConnection:
    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path

        self.__connection: Optional[Connection] = None
        self.__cursor: Optional[Cursor] = None

    @property
    def connection(self) -> Connection:
        if not self.__connection:
            logger.warning("Connection is not established.")
            raise RuntimeError("Connection is not established.")
        return self.__connection
    
    @property
    def cursor(self) -> Cursor:
        if not self.__cursor:
            logger.warning("Cursor is not established.")
            raise RuntimeError("Cursor is not established.")
        return self.__cursor

    def __enter__(self):
        logger.info("Creating a connection and adding rules.")

        self.__connection = connect(self.file_path)

        self.__connection.execute("PRAGMA journal_mode=WAL")
        self.__connection.execute("PRAGMA synchronous=NORMAL")
        self.__connection.execute("PRAGMA cache_size=65536")
        self.__connection.execute("PRAGMA temp_store=MEMORY")
        if platform != "win32":
            self.__connection.execute("PRAGMA mmap_size=268435456")

        self.__cursor = self.__connection.cursor()

        logger.info("Connection established.")

        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional["TracebackType"],
    ) -> Optional[bool]:
        if self.__connection:
            try:
                # Commit transaction
                if exc_type is None:
                    try:
                        self.__connection.commit()
                    except Exception as _:
                        logger.error("Failed to commit transaction.", exc_info=True)
                        try:
                            self.__connection.rollback()
                        except Exception as _:
                            pass

                # Rollback transaction
                else:
                    try:
                        self.__connection.rollback()
                    except Exception as _:
                        logger.error("Failed to rollback transaction.", exc_info=True)

            finally:
                try:
                    self.__connection.close()
                except Exception as _:
                    logger.error("Failed to close connection.", exc_info=True)
                finally:
                    self.__connection = None
                    self.__cursor = None

        return False
