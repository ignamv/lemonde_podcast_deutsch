"""Fetch audio articles from LeMonde website, store into database"""
import re
import datetime
import requests
from logging import getLogger, basicConfig
from bs4 import BeautifulSoup
from db import get_db


logger = getLogger(__name__)

BASE_URL = "https://monde-diplomatique.de"

session = requests.Session()
db = get_db()


def fetch_months():
    """Fetch HTML for index with links to monthly issues"""
    months_url = BASE_URL + "/archiv-audio"
    logger.info('Fetched months index at %s', months_url)
    return session.get(months_url).text


def mock_months():
    """Mock fetch_months() returning stored HTML"""
    return open("mock/archiv-audio", encoding="iso-8859-15").read()


def parse_months(body):
    """Parse HTML of issue index, return list of (date, url) pairs"""
    soup = BeautifulSoup(body, "html.parser")

    month_re = re.compile(r"/archiv-audio\?base=lmd_(\d{4})_(\d\d)_(\d\d)")

    ret = []
    for link in soup.find_all("a"):
        match = month_re.match(link.get("href"))
        if not match:
            continue
        year, month, day = map(int, match.groups())
        date = datetime.date(year, month, day)
        ret.append((date, BASE_URL + match.group(0)))
    return ret


def fetch_month(url):
    """Fetch HTML for the index of a single issue"""
    logger.info('Fetched month index at %s', url)
    return session.get(url).text


def mock_month():
    """Mock fetch_month() returning stored HTML"""
    return open("mock/archiv-audio?base=lmd_2011_10_14", encoding="iso-8859-15").read()


def parse_month(body):
    """Parse single issue index, return list of (title, audio url) pairs"""
    soup = BeautifulSoup(body, "html.parser")
    ret = []
    for article in soup.find_all("article"):
        title = article.div.text
        url = article.audio.get("src")
        ret.append((title, url))
    return ret


def fetch_size(url):
    """Make HEAD request to get size of file in url"""
    return int(session.head(url).headers["Content-length"])


def yield_all_entries(date_filter):
    """Yield entries from all months which pass the `date_filter`

    Yields (date, title, media url, size) tuples

    `date_filter` receives a `datetime.date` and must return True if the issue is
    to be downloaded
    """
    for date, url in sorted(parse_months(fetch_months())):
        if not date_filter(date):
            continue
        for title, mediaurl in parse_month(fetch_month(url)):
            size = fetch_size(mediaurl)
            logger.info('Fetched entry %s %s', date, title)
            yield date, title, mediaurl, size


def main():
    """Entry point. Returns number of saved entries."""
    last_downloaded_entry_date = db.execute(
        'SELECT max(date) as "maxdate [date]" FROM entries'
    ).fetchone()[0]
    date_filter = lambda date: date > last_downloaded_entry_date
    for entry in yield_all_entries(date_filter):
        db.execute(
            "INSERT INTO entries (date, title, url, size) VALUES (?, ?, ?, ?)", entry
        )
    db.commit()
    logger.info('Wrote %s rows into database', db.total_changes)
    return db.total_changes


if __name__ == "__main__":
    main()
