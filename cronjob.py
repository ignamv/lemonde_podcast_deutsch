"""Fetch new entries, if necessary regenerate feed and upload"""

import os
from pathlib import Path
from subprocess import check_call
from fetch import main as fetch_entries
from generate import main as generate_feed


def main():
    """Entry point"""
    changes = fetch_entries()
    if not changes:
        return
    generate_feed()
    rootdir = Path(__file__).resolve().parent
    os.chdir(rootdir / "output")
    check_call(["git", "add", "feed.xml"])
    check_call(["git", "commit", "--amend", "-m", "Initial commit"])
    check_call(["git", "push", "--force"])
    print("Done")


if __name__ == "__main__":
    main()
