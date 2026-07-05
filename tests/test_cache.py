from pathlib import Path

from cache import Cache


def test_get_returns_none_on_miss(logger, tmp_path):
    cache = Cache(logger, str(tmp_path / "cache"))
    assert cache.get("missing") is None


def test_set_then_get_roundtrip(logger, tmp_path):
    cache = Cache(logger, str(tmp_path / "cache"))
    cache.set("com.example.app", '{"a": 1}')
    assert cache.get("com.example.app") == '{"a": 1}'


def test_set_writes_json_file_named_by_key(logger, tmp_path):
    path = tmp_path / "cache"
    cache = Cache(logger, str(path))
    cache.set("com.example.app", "null")
    assert (path / "com.example.app.json").read_text() == "null"


def test_init_creates_directory(logger, tmp_path):
    target = tmp_path / "nested" / "cache"
    Cache(logger, str(target))
    assert Path(target).is_dir()
