import pytest
import requests

import storeapps
from storeapps import StoreApps
from tests.conftest import FakeResponse

NETFLIX = (
    '{"status":"OK","data":{"apps":[{"app_id":"com.netflix.mediaclient",'
    '"app_name":"Netflix",'
    '"app_page_link":"https://play.google.com/store/apps/details?id=com.netflix.mediaclient",'
    '"price":0}]}}'
)


def test_search_returns_normalized_top_hit(logger, monkeypatch):
    captured = {}

    def fake_get(url, headers=None, params=None, timeout=None):
        captured.update(url=url, headers=headers, params=params, timeout=timeout)
        return FakeResponse(NETFLIX)

    monkeypatch.setattr(storeapps.requests, "get", fake_get)

    result = StoreApps(logger, "SECRET", region="us", language="en").search("Netflix")

    assert result == {
        "app_id": "com.netflix.mediaclient",
        "app_name": "Netflix",
        "url": "https://play.google.com/store/apps/details?id=com.netflix.mediaclient",
        "price": 0,
    }
    assert captured["timeout"] is not None
    assert captured["params"] == {"q": "Netflix", "region": "us", "language": "en", "limit": "1"}
    assert captured["headers"]["x-rapidapi-key"] == "SECRET"
    assert captured["headers"]["x-rapidapi-host"] == "store-apps.p.rapidapi.com"


def test_search_builds_url_when_link_missing(logger, monkeypatch):
    body = '{"data":{"apps":[{"app_id":"com.x.y","app_name":"XY","price":3}]}}'
    monkeypatch.setattr(storeapps.requests, "get", lambda *a, **k: FakeResponse(body))

    result = StoreApps(logger, "K").search("XY")

    assert result == {
        "app_id": "com.x.y",
        "app_name": "XY",
        "url": "https://play.google.com/store/apps/details?id=com.x.y",
        "price": 3,
    }


def test_search_returns_none_when_empty(logger, monkeypatch):
    monkeypatch.setattr(storeapps.requests, "get", lambda *a, **k: FakeResponse('{"data":{"apps":[]}}'))
    assert StoreApps(logger, "K").search("nope") is None


def test_search_raises_on_http_error(logger, monkeypatch):
    monkeypatch.setattr(storeapps.requests, "get", lambda *a, **k: FakeResponse(error=requests.HTTPError("boom")))
    with pytest.raises(requests.HTTPError):
        StoreApps(logger, "K").search("Netflix")


def test_search_defaults_null_price_to_zero(logger, monkeypatch):
    body = '{"data":{"apps":[{"app_id":"com.x.y","app_name":"XY","app_page_link":"u","price":null}]}}'
    monkeypatch.setattr(storeapps.requests, "get", lambda *a, **k: FakeResponse(body))
    assert StoreApps(logger, "K").search("XY")["price"] == 0
