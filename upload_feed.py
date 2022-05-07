"""Upload feed"""
import os
from pathlib import Path
from subprocess import check_call
from logging import getLogger


logger = getLogger(__name__)

__all__ = ["upload_feed"]


def upload_feed():
    """Upload feed"""
    logger.info("Uploading new feed")
    rootdir = Path(__file__).resolve().parent
    os.chdir(rootdir / "output")
    check_call(["git", "add", "feed.xml"])
    check_call(["git", "commit", "--amend", "-m", "Initial commit"])
    check_call(["git", "push", "--force"])
    logger.info("New feed uploaded")


if __name__ == "__main__":
    upload_feed()
