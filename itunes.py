from logging import Logger

import requests


class Itunes:
    """Resolve an Apple App Store app name from its bundle identifier."""

    __logger: Logger
    __country: str
    __api_url: str = "https://itunes.apple.com/lookup"

    def __init__(self, logger: Logger, country: str = "us") -> None:
        self.__logger = logger
        self.__country = country

    def lookup_name(self, bundle_id: str) -> str | None:
        """Return the App Store name for a bundle id, or None if not found."""

        self.__logger.debug(f"Looking up {bundle_id}")

        query = {"bundleId": bundle_id, "country": self.__country}
        r = requests.get(self.__api_url, params=query, timeout=30)
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results:
            return None
        return results[0].get("trackName")
