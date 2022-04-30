"""Migrate old csv entries to sqlite3"""
import pandas as pd
from db import get_db

df = pd.read_csv("entries.csv")
df["date"] = pd.to_datetime(df[["year", "month", "day"]])
df["size"] = 0
df["idx"] = range(len(df))
with get_db() as conn:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS entries (
    idx INTEGER PRIMARY KEY AUTOINCREMENT,
    date TIMESTAMP,
    title TEXT,
    url TEXT,
    size INTEGER
    );"""
    )
    # conn.execute('CREATE INDEX ix_entries_idx ON entries (idx)')
    conn.execute("CREATE INDEX ix_entries_date ON entries (date)")

    df[["idx", "date", "title", "url", "size"]].to_sql(
        "entries", conn, if_exists="append", index=False
    )
