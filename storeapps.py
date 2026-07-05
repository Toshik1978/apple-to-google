from collections.abc import Mapping
from logging import Logger

import requests


class StoreApps:
    """Search Google Play via the RapidAPI Store Apps API."""

    __logger: Logger
    __headers: Mapping[str, str]
    __region: str
    __language: str
    __api_url: str = "https://store-apps.p.rapidapi.com/search"

    def __init__(self, logger: Logger, api_key: str, region: str = "us", language: str = "en") -> None:
        self.__logger = logger
        self.__headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "store-apps.p.rapidapi.com",
        }
        self.__region = region
        self.__language = language

    def search(self, term: str) -> dict | None:
        """Return the top Google Play match for a name, or None if none found."""

        self.__logger.debug(f"Searching {term}")

        query = {"q": term, "region": self.__region, "language": self.__language, "limit": "1"}
        r = requests.get(self.__api_url, headers=self.__headers, params=query, timeout=30)
        r.raise_for_status()
        apps = r.json().get("data", {}).get("apps", [])
        if not apps:
            return None
        top = apps[0]
        app_id = top["app_id"]
        return {
            "app_id": app_id,
            "app_name": top["app_name"],
            "url": top.get("app_page_link") or f"https://play.google.com/store/apps/details?id={app_id}",
            "price": top.get("price") or 0,
        }
