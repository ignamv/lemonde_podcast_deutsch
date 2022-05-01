"""Fetch new entries, if necessary regenerate feed and upload"""

import os
from pathlib import Path
from subprocess import check_call
from fetch import main as fetch_entries
from generate import main as generate_feed
from logging import getLogger, basicConfig, INFO


logger = getLogger(__name__)


def main():
    """Entry point"""
    basicConfig(level=INFO, format='%(levelname)s %(name)s %(asctime)s %(message)s')
    changes = fetch_entries()
    if not changes:
        logger.info('No new entries, exiting')
        return
    generate_feed()
    logger.info('Uploading new feed')
    rootdir = Path(__file__).resolve().parent
    os.chdir(rootdir / "output")
    check_call(["git", "add", "feed.xml"])
    check_call(["git", "commit", "--amend", "-m", "Initial commit"])
    check_call(["git", "push", "--force"])
    logger.info('New feed uploaded')


if __name__ == "__main__":
    main()
