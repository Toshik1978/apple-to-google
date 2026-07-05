#!/usr/bin/env python
import csv
import logging
from pathlib import Path

import click
from dotenv import load_dotenv

from apps import AppCollection
from rapidapi import RapidAPI
from rapidapicache import RapidAPICache


@click.command()
@click.option("--cache", default=".cache", type=click.Path(exists=False), help="Cache directory")
@click.option("--key", help="RapidAPI API key", required=True, envvar="RAPID_API_KEY")
@click.option("-v", default=False, is_flag=True, help="Verbose logging", required=False)
@click.argument("filename", type=click.Path(exists=True), required=True)
def main(cache, key, v, filename):
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG if v else logging.INFO)
    logger = logging.getLogger(__name__)

    coll = AppCollection(logger, RapidAPI(logger, key), RapidAPICache(logger, cache))
    # Add all applications to the collection
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                coll.add(row["CFBundleIdentifier"])
            except Exception as e:
                logger.debug(f"Failed to add application: {e}")

    # Generate new CSV
    p = Path(filename)
    p = p.with_stem(p.stem + ".android")
    with p.open(mode="w") as newfile:
        writer = csv.writer(newfile)
        apps = coll.get_apps()
        for app in apps:
            matches = apps[app]
            if not matches:
                logger.debug(f"No Google Play match for {app}, skipping")
                continue
            match = matches[0]
            writer.writerow(
                [
                    app,
                    match["id"],
                    match["name"],
                    match["url"],
                    match["currentVersion"],
                    match["price"]["raw"],
                ]
            )


# main block
if __name__ == "__main__":
    load_dotenv()
    main()
