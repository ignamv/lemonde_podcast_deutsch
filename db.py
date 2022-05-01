"""Database connection"""
import sqlite3
import datetime


def convert_date(bytes_):
    """Convert sqlite3 timestamp into datetime.datetime"""
    return datetime.datetime.fromisoformat(bytes_.decode()).date()


def adapt_date(date):
    """Convert datetime.date to bytes"""
    return date.isoformat().encode("ascii")


sqlite3.register_converter("date", convert_date)
sqlite3.register_adapter("date", adapt_date)


def get_db():
    """Connect to database"""
    conn = sqlite3.connect(
        "db/db.sqlite3", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )
    return conn
