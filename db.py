"""Database connection"""
import sqlite3


def get_db():
    """Connect to database"""
    return sqlite3.connect("db/db.sqlite3")
