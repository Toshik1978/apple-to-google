[![CI](https://github.com/Toshik1978/apple-to-google/actions/workflows/ci.yml/badge.svg)](https://github.com/Toshik1978/apple-to-google/actions)
![Tests](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/Toshik1978/GIST_ID_PLACEHOLDER/raw/tests.json&maxAge=180)
![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/Toshik1978/GIST_ID_PLACEHOLDER/raw/coverage.json&maxAge=180)

# Apple → Google app finder

A command-line tool that finds Android (Google Play) analogues for your Apple App Store apps.

Give it a CSV exported from Apple (with a `CFBundleIdentifier` column). For each app it searches
Google Play through the [RapidAPI app-stores API](https://rapidapi.com/danielamitay/api/app-stores/),
caches every response on disk, and writes a sibling `<name>.android.csv` with the matched Google
Play app id, name, URL, version and price.

## Requirements

- Python 3.14+ and [uv](https://docs.astral.sh/uv/)
- A RapidAPI subscription to the
  [app-stores API](https://rapidapi.com/danielamitay/api/app-stores/)

## Usage

```bash
git clone https://github.com/Toshik1978/apple-to-google
cd apple-to-google

cp .env.dist .env        # put your key in RAPID_API_KEY (or pass --key)
uv run apple-to-google apps.csv
```

This reads `apps.csv` and writes `apps.android.csv` beside it.

### Options

| Option        | Description                                              |
|---------------|----------------------------------------------------------|
| `--key`       | RapidAPI key (overrides `RAPID_API_KEY` from env/`.env`) |
| `--cache DIR` | Cache directory (default `.cache`)                       |
| `-v`          | Verbose logging                                          |
| `FILENAME`    | Input CSV with a `CFBundleIdentifier` column (required)  |

Responses are cached under `--cache`, so re-runs don't re-hit (or re-bill) the API.

## Development

```bash
uv run ruff check .          # lint
uv run ruff format .         # format
uv run pytest --cov          # tests + coverage
```

## License

MIT — see [LICENSE](LICENSE).
