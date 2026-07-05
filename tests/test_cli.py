import csv
import os
import runpy
import sys

import pytest
import requests
from click.testing import CliRunner

import cli as cli_module
from tests.conftest import FakeResponse

ITUNES = {
    "com.example.one": '{"resultCount": 1, "results": [{"trackName": "One"}]}',
    "com.example.empty": '{"resultCount": 0, "results": []}',
}
STORE = {
    "One": (
        '{"data":{"apps":[{"app_id":"com.google.one","app_name":"One",'
        '"app_page_link":"https://play.google.com/store/apps/details?id=com.google.one",'
        '"price":0}]}}'
    ),
}


def _fake_get(url, headers=None, params=None, timeout=None):
    if "itunes.apple.com" in url:
        return FakeResponse(ITUNES[params["bundleId"]])
    return FakeResponse(STORE.get(params["q"], '{"data":{"apps":[]}}'))


def _write_input_csv(path):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["CFBundleIdentifier"])
        writer.writerow(["com.example.one"])
        writer.writerow(["com.example.empty"])


def test_cli_generates_android_csv_and_skips_unmatched(monkeypatch):
    monkeypatch.setattr(requests, "get", _fake_get)
    runner = CliRunner()
    with runner.isolated_filesystem():
        _write_input_csv("apps.csv")

        result = runner.invoke(cli_module.cli, ["--key", "SECRET", "apps.csv"])

        assert result.exit_code == 0, result.output
        with open("apps.android.csv", newline="") as f:
            rows = list(csv.reader(f))

    assert rows == [
        [
            "com.example.one",
            "com.google.one",
            "One",
            "https://play.google.com/store/apps/details?id=com.google.one",
            "0",
        ],
    ]


def test_cli_reads_key_from_env(monkeypatch):
    monkeypatch.setattr(requests, "get", _fake_get)
    monkeypatch.setenv("RAPID_API_KEY", "FROM-ENV")
    runner = CliRunner()
    with runner.isolated_filesystem():
        _write_input_csv("apps.csv")
        result = runner.invoke(cli_module.cli, ["apps.csv"])
        assert result.exit_code == 0, result.output
        with open("apps.android.csv", newline="") as f:
            rows = list(csv.reader(f))
    assert rows[0][0] == "com.example.one"


def test_cli_reads_key_from_dotenv_file(monkeypatch):
    monkeypatch.setattr(requests, "get", _fake_get)
    monkeypatch.delenv("RAPID_API_KEY", raising=False)
    monkeypatch.setattr(sys, "argv", ["apple-to-google", "apps.csv"])
    runner = CliRunner()
    try:
        with runner.isolated_filesystem():
            _write_input_csv("apps.csv")
            with open(".env", "w") as f:
                f.write("RAPID_API_KEY=FROM-DOTENV\n")

            with pytest.raises(SystemExit) as exc_info:
                cli_module.main()

            assert exc_info.value.code == 0
            with open("apps.android.csv", newline="") as f:
                rows = list(csv.reader(f))
        assert rows[0][0] == "com.example.one"
    finally:
        os.environ.pop("RAPID_API_KEY", None)


def test_cli_passes_region_and_lang(monkeypatch):
    seen = {}

    def capture_get(url, headers=None, params=None, timeout=None):
        if "store-apps" in url:
            seen.update(region=params.get("region"), language=params.get("language"))
        return _fake_get(url, headers=headers, params=params, timeout=timeout)

    monkeypatch.setattr(requests, "get", capture_get)
    runner = CliRunner()
    with runner.isolated_filesystem():
        _write_input_csv("apps.csv")
        result = runner.invoke(cli_module.cli, ["--key", "K", "--region", "de", "--lang", "de", "apps.csv"])
        assert result.exit_code == 0, result.output
    assert seen == {"region": "de", "language": "de"}


def test_cli_skips_row_that_fails_to_add(monkeypatch):
    monkeypatch.setattr(requests, "get", _fake_get)
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("apps.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["SomeOtherColumn"])
            writer.writerow(["irrelevant"])

        result = runner.invoke(cli_module.cli, ["--key", "K", "apps.csv"])

        assert result.exit_code == 0, result.output
        with open("apps.android.csv", newline="") as f:
            rows = list(csv.reader(f))
    assert rows == []


def test_main_module_entrypoint(monkeypatch):
    monkeypatch.setattr(requests, "get", _fake_get)
    monkeypatch.setenv("RAPID_API_KEY", "FROM-ENV")
    runner = CliRunner()
    with runner.isolated_filesystem():
        _write_input_csv("apps.csv")
        monkeypatch.setattr(sys, "argv", ["apple-to-google", "apps.csv"])
        with pytest.raises(SystemExit) as exc_info:
            runpy.run_module("cli", run_name="__main__")
        assert exc_info.value.code == 0
