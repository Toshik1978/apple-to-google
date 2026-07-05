import json
from logging import Logger

from rapidapi import RapidAPI
from rapidapicache import RapidAPICache


class AppCollection:
    """Collection of applications."""

    __logger: Logger
    __api: RapidAPI
    __cache: RapidAPICache
    __apps: dict[str, dict]

    def __init__(self, logger: Logger, api: RapidAPI, cache: RapidAPICache) -> None:
        self.__logger = logger
        self.__api = api
        self.__cache = cache
        self.__apps = {}

    def get_apps(self) -> dict[str, dict]:
        """Get Android applications."""
        return self.__apps

    def add(self, app_name: str) -> None:
        """Add application to the collection."""

        # Try to get data from the cache
        app = self.__cache.get(app_name)
        if app is None:
            # Use RapidAPI if no data in a cache and save it in the cache then
            app = self.__api.search(app_name)
            self.__cache.set(app_name, app)

        self.__apps[app_name] = json.loads(app)
