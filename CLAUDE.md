# CLAUDE.md

Guidance for working in this repository.

## What this project is

A Click CLI that finds Android (Google Play) analogues for Apple App Store apps. It reads an
Apple export CSV (a `CFBundleIdentifier` column), searches Google Play for each app via RapidAPI
(danielamitay `app-stores`), caches every response on disk, and writes a sibling
`<name>.android.csv` with the matched Google Play id, name, url, version and price. Python 3.14+,
managed with `uv`.

## Commands

This is an installable project (hatchling build backend) exposing the `apple-to-google` console
script. `uv run` builds/installs it into a managed env automatically. Dependencies live in **one
place**: `pyproject.toml`.

```bash
cp .env.dist .env            # fill in RAPID_API_KEY (or pass --key)
uv run apple-to-google apps.csv          # writes apps.android.csv
uv run apple-to-google --key <KEY> --cache .cache -v apps.csv
```

`RAPID_API_KEY` comes from an env var or a `.env` file (`load_dotenv()`); `--key` overrides it.
Subscribe to the API at https://rapidapi.com/danielamitay/api/app-stores/.

### Quality checks

```bash
uv run ruff check .          # lint
uv run ruff format .         # format (config: line-length 120, rules E/F/I/UP/B)
uv run pytest                # tests (tests/)
uv run pytest --cov          # tests + coverage (config in [tool.coverage.run])
```

CI (`.github/workflows/ci.yml`) runs `ruff check`, `ruff format --check`, and `pytest --cov` on
push to `main` and on PRs. There is no coverage gate (the badge is informational). On push to
`main` it publishes Tests/Coverage badges by updating a gist (README badge URLs). This needs repo
secrets `GIST_ID` and `GIST_SECRET_TOKEN` (a PAT with `gist` scope, created by a maintainer).
`.github/workflows/secret-scan.yml` runs gitleaks on push/PR.

## Architecture

The entry point is `cli.py`; `cli:main` is a thin wrapper that calls `load_dotenv()` then the
Click command `cli`. Three modules behind it:

- **`rapidapi.py`** — `RapidAPI` wraps the RapidAPI `app-stores` search endpoint. `search(term)`
  returns the raw JSON response text. Every outbound call passes an explicit `timeout`.
- **`rapidapicache.py`** — `RapidAPICache` is an on-disk JSON cache keyed by bundle id
  (`<path>/<key>.json`). `get` returns the cached text or `None`; `set` writes it. The cache dir
  is created on construction.
- **`apps.py`** — `AppCollection` ties them together: `add(bundle_id)` returns cached text if
  present, otherwise calls the API and caches the result, then stores `json.loads(...)` (a list of
  match dicts) under the bundle id. `get_apps()` returns `{bundle_id: [match, ...]}`.

`cli.py` reads the input CSV (`CFBundleIdentifier` per row, failures logged at debug and skipped),
then writes `<name>.android.csv` using the **first** match per app. Apps whose search returned no
matches are skipped (empty list — do not index `[0]`).

## Conventions

- Python >= 3.14. Modern typing (`str | None`, builtin generics).
- "Private" name-mangled attributes (`self.__x`) and class-level type annotations documenting
  structure.
- Network calls use `requests` with an explicit `timeout` — keep timeouts on any new call.
- Flat layout: top-level modules (`cli.py`, `apps.py`, `rapidapi.py`, `rapidapicache.py`), all
  listed in `[tool.hatch.build.targets.wheel].only-include`. Add new modules there or they won't
  ship in the wheel. Imports are absolute (`from apps import ...`).
- Secrets (`.env`, `RAPID_API_KEY`) must never be committed.

## Git conventions

- **Never add `Co-Authored-By` trailers** (or any AI attribution) to commit messages.

## Gotchas when editing

- New top-level modules must be added to `only-include` in `pyproject.toml`.
- The API can return an empty match list for an app; the writer must skip it rather than index
  `[0]` (that was a real crash).
- Cache keys are raw bundle ids used as filenames; they already contain dots, not path separators.
