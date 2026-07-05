import json

from apps import AppCollection

RECORD = {"app_id": "com.netflix.mediaclient", "app_name": "Netflix", "url": "u", "price": 0}


class FakeItunes:
    def __init__(self, name: str | None) -> None:
        self.name = name
        self.calls = 0

    def lookup_name(self, bundle_id: str) -> str | None:
        self.calls += 1
        return self.name


class FakeStoreApps:
    def __init__(self, record: dict | None) -> None:
        self.record = record
        self.calls = 0

    def search(self, term: str) -> dict | None:
        self.calls += 1
        return self.record


class FakeCache:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self.store.get(key)

    def set(self, key: str, value: str) -> None:
        self.store[key] = value


def test_add_on_miss_resolves_and_caches(logger):
    itunes = FakeItunes("Netflix")
    storeapps = FakeStoreApps(RECORD)
    cache = FakeCache()
    coll = AppCollection(logger, itunes, storeapps, cache)

    coll.add("com.netflix.Netflix")

    assert itunes.calls == 1
    assert storeapps.calls == 1
    assert coll.get_apps() == {"com.netflix.Netflix": RECORD}
    assert json.loads(cache.store["com.netflix.Netflix"]) == RECORD


def test_add_on_hit_skips_both_adapters(logger):
    itunes = FakeItunes("should-not-be-used")
    storeapps = FakeStoreApps(RECORD)
    cache = FakeCache()
    cache.set("com.netflix.Netflix", '{"app_id": "cached", "app_name": "Cached", "url": "u", "price": 0}')
    coll = AppCollection(logger, itunes, storeapps, cache)

    coll.add("com.netflix.Netflix")

    assert itunes.calls == 0
    assert storeapps.calls == 0
    assert coll.get_apps()["com.netflix.Netflix"]["app_id"] == "cached"


def test_add_with_no_app_store_entry_records_none_and_skips_search(logger):
    itunes = FakeItunes(None)
    storeapps = FakeStoreApps(RECORD)
    cache = FakeCache()
    coll = AppCollection(logger, itunes, storeapps, cache)

    coll.add("com.unknown.app")

    assert itunes.calls == 1
    assert storeapps.calls == 0
    assert coll.get_apps() == {"com.unknown.app": None}
    assert cache.store["com.unknown.app"] == "null"


def test_add_with_no_play_match_records_none(logger):
    itunes = FakeItunes("Obscure App")
    storeapps = FakeStoreApps(None)
    cache = FakeCache()
    coll = AppCollection(logger, itunes, storeapps, cache)

    coll.add("com.obscure.app")

    assert itunes.calls == 1
    assert storeapps.calls == 1
    assert coll.get_apps() == {"com.obscure.app": None}
