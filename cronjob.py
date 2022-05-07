"""Fetch new entries, if necessary regenerate feed and upload"""
from logging import getLogger, basicConfig, INFO
from fetch_to_database import fetch_entries_to_database
from generate import generate_feed
from upload_feed import upload_feed


logger = getLogger(__name__)


def main():
    """Entry point"""
    basicConfig(level=INFO, format="%(levelname)s %(name)s %(asctime)s %(message)s")
    changes = fetch_entries_to_database()
    if not changes:
        logger.info("No new entries, exiting")
        return
    generate_feed()
    upload_feed()


if __name__ == "__main__":
    main()
