import json
import logging

import pytest


@pytest.fixture
def logger() -> logging.Logger:
    return logging.getLogger("apple-to-google-test")


class FakeResponse:
    """Minimal stand-in for a requests.Response."""

    def __init__(self, text: str = "[]", error: Exception | None = None) -> None:
        self.text = text
        self.__error = error

    def raise_for_status(self) -> None:
        if self.__error is not None:
            raise self.__error

    def json(self) -> object:
        return json.loads(self.text)
