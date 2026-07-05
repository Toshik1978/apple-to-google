[![CI](https://github.com/Toshik1978/apple-to-google/actions/workflows/ci.yml/badge.svg)](https://github.com/Toshik1978/apple-to-google/actions)
![Tests](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/Toshik1978/97986d66320283efb97842821be828aa/raw/tests.json&maxAge=180)
![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/Toshik1978/97986d66320283efb97842821be828aa/raw/coverage.json&maxAge=180)

# Apple → Google app finder

A command-line tool that finds Android (Google Play) analogues for your Apple App Store apps.

Give it a CSV exported from Apple (with a `CFBundleIdentifier` column). For each app it searches
Google Play through the [RapidAPI app-stores API](https://rapidapi.com/danielamitay/api/app-stores/),
caches every response on disk, and writes a sibling `<name>.android.csv` with the matched Google
Play app id, name, URL, version and price.

## Why I built this

I was on Apple for **10 years**, and over that time I'd accumulated a whole set of apps I relied on
day to day. When I started thinking about moving to Android, the real question wasn't the phone —
it was whether I'd be able to replace all of those apps. I couldn't find a good enough way to check:
going through them one by one, searching Google Play by hand, was slow and error-prone.

So I wrote this. I exported my Apple apps, ran them through the tool, and got back a CSV of the
Google Play equivalents in one pass. It saved a lot of time — but more importantly, it's what
actually made the decision for me. Once I could see that **every app had an Android counterpart
except one**, I knew the migration was safe, and I went ahead with it.

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
