"""Make HTTP requests with logging and rate limiting"""
import datetime
from pathlib import Path
import logging
import time
from requests import Session

session = Session()
logger = logging.getLogger(__name__)
cachedir = Path("cache")


__all__ = [
    "fetch_issue_index",
    "fetch_issue",
    "fetch_article",
    "get_url_size",
]


# pylint: disable=too-few-public-methods
class BackOff:
    """Rate limiter"""

    def __init__(self, delay):
        self.delay = delay
        self.last_request = None

    def __call__(self):
        """Ensure at least `delay` seconds have passed since end of last request"""
        if self.last_request is not None:
            remaining = self.delay - (time.time() - self.last_request)
            if remaining > 0:
                time.sleep(remaining)
        self.last_request = time.time()


back_off = BackOff(delay=3)


def make_url_absolute(url):
    """Add domain name to url if necessary"""
    base_url = "https://monde-diplomatique.de"
    if url[0] == "/":
        url = base_url + url
    return url


def get(url):
    """Log and get url (possibly without domain)"""
    back_off()
    logger.info("GET %s", url)
    return session.get(make_url_absolute(url))


def head(url):
    """Log and request headers for url (possibly without domain)"""
    back_off()
    logger.info("HEAD %s", url)
    return session.head(make_url_absolute(url))


def get_if_not_cached(url, cache_filename, expire=None):
    """Get url contents, or read from cache if available and not expired"""
    if cache_filename.exists():
        last_modified = datetime.datetime.fromtimestamp(cache_filename.stat().st_mtime)
        elapsed = datetime.datetime.now() - last_modified
        if expire is None or elapsed < expire:
            return cache_filename.open().read()
    response = get(url)
    assert response.status_code == 200
    cache_filename.open("w").write(response.text)
    return response.text


def fetch_issue_index():
    """Get HTML for text archive issue index"""
    url = "/archiv-text"
    cachefilename = cachedir / "archiv-text.html"
    return get_if_not_cached(url, cachefilename, datetime.timedelta(days=1))


def fetch_issue(date, url):
    """Get HTML for text archive issue"""
    cachefilename = cachedir / "archiv_text" / date.isoformat()
    return get_if_not_cached(url, cachefilename)


def fetch_article(id_, url):
    """Get HTML for text archive article"""
    cachefilename = cachedir / "archiv_text_articles" / str(id_)
    return get_if_not_cached(url, cachefilename)


def get_url_size(url):
    """Make HEAD request to get size of file in url"""
    return int(head(url).headers["Content-length"])
