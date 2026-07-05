from pathlib import Path

from rapidapicache import RapidAPICache


def test_get_returns_none_on_miss(logger, tmp_path):
    cache = RapidAPICache(logger, str(tmp_path / "cache"))
    assert cache.get("missing") is None


def test_set_then_get_roundtrip(logger, tmp_path):
    cache = RapidAPICache(logger, str(tmp_path / "cache"))
    cache.set("com.example.app", '{"a": 1}')
    assert cache.get("com.example.app") == '{"a": 1}'


def test_set_writes_json_file_named_by_key(logger, tmp_path):
    path = tmp_path / "cache"
    cache = RapidAPICache(logger, str(path))
    cache.set("com.example.app", "[]")
    assert (path / "com.example.app.json").read_text() == "[]"


def test_init_creates_directory(logger, tmp_path):
    target = tmp_path / "nested" / "cache"
    RapidAPICache(logger, str(target))
    assert Path(target).is_dir()
