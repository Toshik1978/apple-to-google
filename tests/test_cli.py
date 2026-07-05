import csv
import json
import runpy
import sys

import pytest
from click.testing import CliRunner

import cli as cli_module
import rapidapi
from tests.conftest import FakeResponse

RESPONSES = {
    "com.example.one": json.dumps(
        [
            {
                "id": "com.google.one",
                "name": "One",
                "url": "https://play.google.com/one",
                "currentVersion": "1.2.3",
                "price": {"raw": 0},
            }
        ]
    ),
    "com.example.empty": json.dumps([]),  # search returned nothing
}


def _fake_get(url, headers=None, params=None, timeout=None):
    return FakeResponse(RESPONSES[params["term"]])


def _write_input_csv(path):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["CFBundleIdentifier"])
        writer.writerow(["com.example.one"])
        writer.writerow(["com.example.empty"])


def test_cli_generates_android_csv_and_skips_empty(monkeypatch):
    monkeypatch.setattr(rapidapi.requests, "get", _fake_get)
    runner = CliRunner()
    with runner.isolated_filesystem():
        _write_input_csv("apps.csv")

        result = runner.invoke(cli_module.main, ["--key", "SECRET", "apps.csv"])

        assert result.exit_code == 0, result.output
        with open("apps.android.csv", newline="") as f:
            rows = list(csv.reader(f))

    # Only the app with a real result is written; the empty one is skipped, not a crash.
    assert rows == [["com.example.one", "com.google.one", "One", "https://play.google.com/one", "1.2.3", "0"]]


def test_cli_reads_key_from_env(monkeypatch):
    monkeypatch.setattr(rapidapi.requests, "get", _fake_get)
    monkeypatch.setenv("RAPID_API_KEY", "FROM-ENV")
    runner = CliRunner()
    with runner.isolated_filesystem():
        _write_input_csv("apps.csv")

        # No --key on the command line; it must come from the env var.
        result = runner.invoke(cli_module.main, ["apps.csv"])

        assert result.exit_code == 0, result.output
        # No --key was passed; success proves the key came from RAPID_API_KEY.
        with open("apps.android.csv", newline="") as f:
            rows = list(csv.reader(f))
    assert rows[0][0] == "com.example.one"


def test_cli_skips_row_that_fails_to_add(monkeypatch):
    # A row missing the expected column raises when accessed by key; the CLI
    # logs and continues instead of crashing.
    monkeypatch.setattr(rapidapi.requests, "get", _fake_get)
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("apps.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["SomeOtherColumn"])
            writer.writerow(["irrelevant"])

        result = runner.invoke(cli_module.main, ["--key", "SECRET", "apps.csv"])

        assert result.exit_code == 0, result.output
        with open("apps.android.csv", newline="") as f:
            rows = list(csv.reader(f))
    assert rows == []


def test_main_block_loads_dotenv_and_invokes_main(monkeypatch):
    # Exercises the `if __name__ == "__main__":` guard (load_dotenv() + main()).
    monkeypatch.setattr(rapidapi.requests, "get", _fake_get)
    monkeypatch.setenv("RAPID_API_KEY", "FROM-ENV")
    runner = CliRunner()
    with runner.isolated_filesystem():
        _write_input_csv("apps.csv")
        monkeypatch.setattr(sys, "argv", ["cli.py", "apps.csv"])

        with pytest.raises(SystemExit) as exc_info:
            runpy.run_module("cli", run_name="__main__")

        assert exc_info.value.code == 0
        with open("apps.android.csv", newline="") as f:
            rows = list(csv.reader(f))
    assert rows[0][0] == "com.example.one"
