import os.path
from logging import Logger
from pathlib import Path


class RapidAPICache:
    """Cache for application information from RapidAPI responses."""

    __logger: Logger
    __path: str

    def __init__(self, logger: Logger, path: str) -> None:
        self.__logger = logger
        self.__path = path

        Path(self.__path).mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> str | None:
        """Get value from cache."""

        p = Path(self.__filename(key))
        if p.is_file():
            self.__logger.debug(f"Reading from cache: {key}")
            return p.read_text()
        return None

    def set(self, key: str, value: str) -> None:
        """Set value in cache."""

        self.__logger.debug(f"Writing to cache: {key}")
        Path(self.__filename(key)).write_text(value)

    def __filename(self, key: str) -> str:
        """Get filename for key in cache."""

        return os.path.join(self.__path, key + ".json")
