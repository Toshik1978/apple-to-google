from logging import Logger
from typing import Mapping

import requests


class RapidAPI:
    """Rapid API wrapper."""

    __logger: Logger
    __headers: Mapping[str, str]
    __api_url: str = "https://app-stores.p.rapidapi.com/search"

    def __init__(self, logger: Logger, api_key: str) -> None:
        self.__logger = logger
        self.__headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "app-stores.p.rapidapi.com"
        }

    def search(self, app_name: str) -> str:
        """Search application in Google Play by query."""

        self.__logger.debug(f"Searching {app_name}")

        query = {"language": "en", "store": "google", "term": app_name}
        r = requests.get(self.__api_url, headers=self.__headers, params=query)
        r.raise_for_status()
        return r.text
