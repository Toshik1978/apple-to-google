from apps import AppCollection


class FakeAPI:
    def __init__(self, text: str) -> None:
        self.text = text
        self.calls = 0

    def search(self, app_name: str) -> str:
        self.calls += 1
        return self.text


class FakeCache:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self.store.get(key)

    def set(self, key: str, value: str) -> None:
        self.store[key] = value


def test_add_on_cache_miss_calls_api_and_caches(logger):
    api = FakeAPI('[{"id": "com.google.one"}]')
    cache = FakeCache()
    coll = AppCollection(logger, api, cache)

    coll.add("com.example.one")

    assert api.calls == 1
    assert cache.store["com.example.one"] == '[{"id": "com.google.one"}]'
    assert coll.get_apps() == {"com.example.one": [{"id": "com.google.one"}]}


def test_add_on_cache_hit_skips_api(logger):
    api = FakeAPI('[{"id": "should-not-be-used"}]')
    cache = FakeCache()
    cache.set("com.example.one", '[{"id": "com.google.cached"}]')
    coll = AppCollection(logger, api, cache)

    coll.add("com.example.one")

    assert api.calls == 0
    assert coll.get_apps() == {"com.example.one": [{"id": "com.google.cached"}]}
