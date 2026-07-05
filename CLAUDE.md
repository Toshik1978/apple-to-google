# CLAUDE.md

Guidance for working in this repository.

## What this project is

A Click CLI that finds Android (Google Play) analogues for Apple App Store apps. It reads an Apple
export CSV (a `CFBundleIdentifier` column), looks up each app's name via Apple's free iTunes Lookup
API, finds the matching Google Play app via the RapidAPI **Store Apps** API, caches every resolved
match on disk, and writes a sibling `<name>.android.csv` with the matched Google Play id, name, URL
and price. Python 3.14+, managed with `uv`.

## Commands

This is an installable project (hatchling build backend) exposing the `apple-to-google` console
script. `uv run` builds/installs it into a managed env automatically. Dependencies live in **one
place**: `pyproject.toml`.

```bash
cp .env.dist .env            # fill in RAPID_API_KEY (or pass --key)
uv run apple-to-google apps.csv                       # writes apps.android.csv
uv run apple-to-google --key <KEY> --region de --lang de -v apps.csv
```

`RAPID_API_KEY` comes from an env var or a `.env` file (`load_dotenv(find_dotenv(usecwd=True))` in
`cli.main`, run before Click parses); `--key` overrides. Subscribe to the Store Apps API free tier
at https://rapidapi.com/letscrape-6bRBa3QguO5/api/store-apps (100 requests/month).

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

The entry point is `cli.py` — `cli:main` is a thin wrapper that runs `load_dotenv(...)` then the
Click command `cli`. Three adapters behind it:

- **`itunes.py`** — `Itunes.lookup_name(bundle_id)` resolves an Apple bundle id to its App Store
  name via `https://itunes.apple.com/lookup` (`requests`, explicit `timeout`), keyless. Returns
  `None` when the App Store has no such app.
- **`storeapps.py`** — `StoreApps.search(name)` returns the top Google Play match as
  `{app_id, app_name, url, price}` via the RapidAPI Store Apps `/search` (`limit=1`), or `None`.
  `url` is the API's `app_page_link` (falling back to a constructed details URL). Needs the RapidAPI
  key.
- **`cache.py`** — `Cache` is an on-disk JSON cache keyed by bundle id (`<path>/<key>.json`). It
  stores the final resolved record (a dict, or JSON `null` for "no match"), so re-runs skip both
  network calls.
- **`apps.py`** — `AppCollection` orchestrates: `add(bundle_id)` returns the cached record if present,
  else resolves the name via iTunes → searches Store Apps → caches the record. `get_apps()` returns
  `{bundle_id: record | None}`.

`cli.py` reads the input CSV (`CFBundleIdentifier` per row, failures logged at debug and skipped),
then writes `<name>.android.csv` (no header, 5 columns) for each matched app, skipping `None` records.

## Conventions

- Python >= 3.14. Modern typing (`str | None`, builtin generics).
- "Private" name-mangled attributes (`self.__x`) and class-level type annotations.
- Network calls use `requests` with an explicit `timeout` — keep timeouts on any new call.
- Flat layout: top-level modules (`cli.py`, `apps.py`, `itunes.py`, `storeapps.py`, `cache.py`), all
  listed in `[tool.hatch.build.targets.wheel].only-include`. Add new modules there or they won't ship.
  Imports are absolute (`from itunes import ...`).
- Secrets (`.env`, `RAPID_API_KEY`) must never be committed.

## Git conventions

- **Never add `Co-Authored-By` trailers** (or any AI attribution) to commit messages.

## Gotchas when editing

- New top-level modules must be added to `only-include` in `pyproject.toml`.
- iTunes lookup and Store Apps search can each legitimately return "nothing"; both map to a `None`
  record and the app is skipped in the output rather than crashing.
- A `None` (no-match) result is cached too, so a not-found app isn't re-queried — clear `--cache`
  to force a re-query.
- Store Apps free tier is 100 requests/month; one request per uncached app (iTunes lookups are free).
