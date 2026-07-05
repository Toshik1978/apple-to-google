import pytest
import requests

import rapidapi
from rapidapi import RapidAPI
from tests.conftest import FakeResponse


def test_search_passes_timeout_and_builds_request(logger, monkeypatch):
    captured = {}

    def fake_get(url, headers=None, params=None, timeout=None):
        captured.update(url=url, headers=headers, params=params, timeout=timeout)
        return FakeResponse('[{"id": "x"}]')

    monkeypatch.setattr(rapidapi.requests, "get", fake_get)

    result = RapidAPI(logger, "SECRET").search("com.example.app")

    assert result == '[{"id": "x"}]'
    assert captured["timeout"] is not None  # hardening: never a hanging call
    assert captured["params"] == {"language": "en", "store": "google", "term": "com.example.app"}
    assert captured["headers"]["x-rapidapi-key"] == "SECRET"
    assert captured["headers"]["x-rapidapi-host"] == "app-stores.p.rapidapi.com"


def test_search_raises_on_http_error(logger, monkeypatch):
    def fake_get(url, headers=None, params=None, timeout=None):
        return FakeResponse(error=requests.HTTPError("boom"))

    monkeypatch.setattr(rapidapi.requests, "get", fake_get)

    with pytest.raises(requests.HTTPError):
        RapidAPI(logger, "SECRET").search("com.example.app")
