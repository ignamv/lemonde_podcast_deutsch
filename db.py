"""Database access"""
import sqlite3
import datetime
from typing import Iterator, Dict, Any, Optional
from lemondetypes import Article, ArticleSummary, UrlSize


__all__ = [
    "write_article_to_db",
    "get_last_downloaded_date",
    "commit",
    "get_all_articles",
    "get_cached_url_size",
    "save_cached_url_size",
]


def convert_date(bytes_: bytes) -> datetime.date:
    """Convert sqlite3 timestamp into datetime.datetime"""
    return datetime.datetime.fromisoformat(bytes_.decode()).date()


def adapt_date(date: datetime.date) -> bytes:
    """Convert datetime.date to bytes"""
    return date.isoformat().encode("ascii")


sqlite3.register_converter("DATE", convert_date)
sqlite3.register_adapter(datetime.date, adapt_date)


# pylint: disable=too-few-public-methods
class GetDatabase:
    """Connect to database only once"""

    def __init__(self, filename: str):
        self.filename = filename
        self.connection: Optional[sqlite3.Connection] = None

    def __call__(self) -> sqlite3.Connection:
        """Connect to database or reuse connection"""

        if self.connection is None:
            self.connection = sqlite3.connect(
                self.filename,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            )
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON")
        return self.connection


get_db = GetDatabase(filename="db/db.sqlite3")


def get_last_downloaded_date() -> datetime.date:
    """Get date of last downloaded article"""
    return (
        get_db()
        .execute('SELECT max(date) as "maxdate [date]" FROM article')
        .fetchone()[0]
    )


def commit():
    """Commit transaction"""
    get_db().commit()


def get_all_articles() -> Iterator[Article]:
    """Yield sorted articles from database"""
    article_cursor = get_db().execute(
        "SELECT mediasyncid, title, date, summary, url, image_url FROM article ORDER BY date DESC"
    )
    for article_row in article_cursor:
        # Fetch authors
        authors_cursor = get_db().execute(
            "SELECT name FROM author JOIN article_author "
            "ON author.id == article_author.author_id "
            "WHERE article_author.mediasyncid == ?",
            (article_row["mediasyncid"],),
        )
        authors = [row[0] for row in authors_cursor]
        summary = ArticleSummary(
            article_row["mediasyncid"],
            article_row["url"],
            article_row["title"],
            article_row["date"],
            article_row["summary"],
            authors,
        )
        # Fetch audio file metadata
        audiofiles_cursor = get_db().execute(
            "SELECT url, size FROM audiofile WHERE mediasyncid == ?",
            (article_row["mediasyncid"],),
        )
        medias = [UrlSize(row["url"], row["size"]) for row in audiofiles_cursor]
        article = Article(summary, article_row["image_url"], medias)
        yield article


def insert_or_get_author(name: str) -> int:
    """Return author id, insert author into database if necessary"""
    ret = (
        get_db()
        .execute("SELECT id FROM author WHERE name == ? LIMIT 1", (name,))
        .fetchone()
    )
    if ret is not None:
        return ret[0]
    return get_db().execute("INSERT INTO author (name) VALUES (?)", (name,)).lastrowid


def insert_dictionary(table: str, keyvalues: Dict[str, Any]) -> int:
    """Insert row into database"""
    placeholders = ",".join(["?"] * len(keyvalues))
    return (
        get_db()
        .execute(
            f'INSERT INTO {table} ({",".join(keyvalues)}) VALUES ({placeholders})',
            keyvalues.values(),
        )
        .lastrowid
    )


def insert_bare_article(article: Article) -> int:
    """Insert article without authors or audio files. Return mediasyncid"""
    summary = article.summary
    return insert_dictionary(
        "article",
        {
            "mediasyncid": summary.mediasyncid,
            "url": summary.url,
            "title": summary.title,
            "date": summary.date,
            "summary": summary.summary,
            "image_url": article.image_url,
        },
    )


def write_article_to_db(article: Article):
    """Write article (including authors and medias) into database"""
    mediasyncid = insert_bare_article(article)
    author_ids = [insert_or_get_author(name) for name in article.summary.authors]
    for author_id in author_ids:
        link_author_to_article(author_id, mediasyncid)
    for media in article.medias:
        get_db().execute(
            "INSERT INTO audiofile (mediasyncid, url, size) VALUES (?,?,?)",
            (mediasyncid, media.url, media.size),
        )


def link_author_to_article(author_id, mediasyncid):
    """Add existing author to an existing article"""
    get_db().execute(
        "INSERT INTO article_author (mediasyncid, author_id) VALUES (?,?)",
        (mediasyncid, author_id),
    )


def get_cached_url_size(url) -> int:
    """Fetch audio size from database"""
    ret = (
        get_db()
        .execute("SELECT size FROM sizecache WHERE url = ? LIMIT 1", (url,))
        .fetchone()
    )
    if ret is None:
        raise KeyError(url)
    return ret[0]


def save_cached_url_size(url, size):
    """Store size of file at url to database"""
    get_db().execute("INSERT INTO sizecache (url, size) VALUES (?,?)", (url, size))
