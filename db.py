"""Database access"""
import sqlite3
import datetime
import json


__all__ = [
    "write_media_to_db",
    "get_last_downloaded_date",
    "commit",
    "get_all_articles",
]


def convert_date(bytes_):
    """Convert sqlite3 timestamp into datetime.datetime"""
    return datetime.datetime.fromisoformat(bytes_.decode()).date()


def adapt_date(date):
    """Convert datetime.date to bytes"""
    return date.isoformat().encode("ascii")


def convert_json(bytes_):
    """Parse sqlite3 json"""
    return json.loads(bytes_.decode("ascii"))


def adapt_json(obj):
    """Encode object into json bytes"""
    return json.dumps(obj).encode("ascii")


sqlite3.register_converter("DATE", convert_date)
sqlite3.register_adapter(datetime.date, adapt_date)
sqlite3.register_converter("JSON", convert_json)


# pylint: disable=too-few-public-methods
class GetDatabase:
    """Connect to database only once"""

    def __init__(self, filename):
        self.filename = filename
        self.connection = None

    def __call__(self):
        """Connect to database or reuse connection"""

        if self.connection is None:
            self.connection = sqlite3.connect(
                self.filename,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            )
            self.connection.row_factory = sqlite3.Row
        return self.connection


get_db = GetDatabase(filename="db/db.sqlite3")


def write_media_to_db(entry):
    """Insert media file entry into database"""
    entry["authors"] = adapt_json(entry["authors"])
    fields = ",".join(entry)
    placeholders = ",".join("?" * len(entry))
    get_db().execute(
        f"INSERT INTO entries2 ({fields}) VALUES ({placeholders})",
        tuple(entry.values()),
    )


def get_last_downloaded_date():
    """Get date of last downloaded article"""
    return (
        get_db()
        .execute('SELECT max(date) as "maxdate [date]" FROM entries2')
        .fetchone()[0]
    )


def commit():
    """Commit transaction"""
    get_db().commit()


def get_all_articles():
    """Yield sorted articles from database"""
    return get_db().execute(
        "SELECT article_url, title, summary, authors, image_url, audio_url, audio_size, date"
        " FROM entries2 ORDER BY date DESC"
    )
