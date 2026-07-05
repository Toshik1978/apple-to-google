#!/usr/bin/env python
import csv
import logging
from pathlib import Path

import click

from apps import AppCollection
from rapidapi import RapidAPI
from rapidapicache import RapidAPICache


@click.command()
@click.option("--cache", default=".cache", type=click.Path(exists=False), help="Cache directory")
@click.option("--key", help="RapidAPI API key", required=True)
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
            writer.writerow(
                [
                    app,
                    apps[app][0]["id"],
                    apps[app][0]["name"],
                    apps[app][0]["url"],
                    apps[app][0]["currentVersion"],
                    apps[app][0]["price"]["raw"],
                ]
            )


# main block
if __name__ == "__main__":
    main()
