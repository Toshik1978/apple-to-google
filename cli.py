#!/usr/bin/env python
import csv
import logging
from pathlib import Path

import click
from dotenv import find_dotenv, load_dotenv

from apps import AppCollection
from cache import Cache
from itunes import Itunes
from storeapps import StoreApps


@click.command()
@click.option("--cache", default=".cache", type=click.Path(exists=False), help="Cache directory")
@click.option("--key", help="RapidAPI API key (Store Apps)", required=True, envvar="RAPID_API_KEY")
@click.option("--region", default="us", help="App Store / Google Play region (country) code")
@click.option("--lang", default="en", help="Google Play language code")
@click.option("-v", default=False, is_flag=True, help="Verbose logging", required=False)
@click.argument("filename", type=click.Path(exists=True), required=True)
def cli(cache, key, region, lang, v, filename):
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG if v else logging.INFO)
    logger = logging.getLogger(__name__)

    coll = AppCollection(logger, Itunes(logger, region), StoreApps(logger, key, region, lang), Cache(logger, cache))
    # Add all applications to the collection
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                # Use the app name from the CSV if present (e.g. ideviceinstaller's
                # CFBundleDisplayName), else fall back to an App Store lookup.
                name = (row.get("CFBundleDisplayName") or row.get("CFBundleName") or "").strip() or None
                coll.add(row["CFBundleIdentifier"], name)
            except Exception as e:
                logger.debug(f"Failed to add application: {e}")

    # Generate new CSV
    p = Path(filename)
    p = p.with_stem(p.stem + ".android")
    with p.open(mode="w") as newfile:
        writer = csv.writer(newfile)
        apps = coll.get_apps()
        for app in apps:
            match = apps[app]
            if not match:
                logger.debug(f"No Google Play match for {app}, skipping")
                continue
            writer.writerow([app, match["app_id"], match["app_name"], match["url"], match["price"]])


def main():
    # Resolve .env from the current working directory (walking up) BEFORE Click parses,
    # so --key can come from a RAPID_API_KEY in a .env in the dir you run from.
    load_dotenv(find_dotenv(usecwd=True))
    cli()


# main block
if __name__ == "__main__":
    main()
