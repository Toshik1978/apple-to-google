import pytest
import requests

import itunes
from itunes import Itunes
from tests.conftest import FakeResponse


def test_lookup_name_returns_track_name(logger, monkeypatch):
    captured = {}

    def fake_get(url, params=None, timeout=None):
        captured.update(url=url, params=params, timeout=timeout)
        return FakeResponse('{"resultCount": 1, "results": [{"trackName": "Netflix"}]}')

    monkeypatch.setattr(itunes.requests, "get", fake_get)

    name = Itunes(logger, country="us").lookup_name("com.netflix.Netflix")

    assert name == "Netflix"
    assert captured["timeout"] is not None
    assert captured["params"] == {"bundleId": "com.netflix.Netflix", "country": "us"}


def test_lookup_name_returns_none_when_not_found(logger, monkeypatch):
    def fake_get(url, params=None, timeout=None):
        return FakeResponse('{"resultCount": 0, "results": []}')

    monkeypatch.setattr(itunes.requests, "get", fake_get)

    assert Itunes(logger).lookup_name("com.unknown.app") is None


def test_lookup_name_raises_on_http_error(logger, monkeypatch):
    def fake_get(url, params=None, timeout=None):
        return FakeResponse(error=requests.HTTPError("boom"))

    monkeypatch.setattr(itunes.requests, "get", fake_get)

    with pytest.raises(requests.HTTPError):
        Itunes(logger).lookup_name("com.netflix.Netflix")
