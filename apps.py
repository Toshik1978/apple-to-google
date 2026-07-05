import json
from logging import Logger

from cache import Cache
from itunes import Itunes
from storeapps import StoreApps


class AppCollection:
    """Collection of resolved Google Play matches keyed by Apple bundle id."""

    __logger: Logger
    __itunes: Itunes
    __storeapps: StoreApps
    __cache: Cache
    __apps: dict[str, dict | None]

    def __init__(self, logger: Logger, itunes: Itunes, storeapps: StoreApps, cache: Cache) -> None:
        self.__logger = logger
        self.__itunes = itunes
        self.__storeapps = storeapps
        self.__cache = cache
        self.__apps = {}

    def get_apps(self) -> dict[str, dict | None]:
        """Get resolved Google Play matches (None where no match was found)."""
        return self.__apps

    def add(self, bundle_id: str) -> None:
        """Resolve a bundle id to its Google Play match and store it."""

        cached = self.__cache.get(bundle_id)
        if cached is not None:
            self.__apps[bundle_id] = json.loads(cached)
            return

        record = self.__resolve(bundle_id)
        self.__cache.set(bundle_id, json.dumps(record))
        self.__apps[bundle_id] = record

    def __resolve(self, bundle_id: str) -> dict | None:
        name = self.__itunes.lookup_name(bundle_id)
        if not name:
            self.__logger.debug(f"No App Store entry for {bundle_id}")
            return None
        match = self.__storeapps.search(name)
        if match is None:
            self.__logger.debug(f"No Google Play match for {bundle_id} ({name})")
            return None
        return match
