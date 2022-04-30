"""Fetch file sizes from website and write to database"""
import requests
from db import get_db

conn = get_db()

with requests.Session() as session:
    for row in conn.execute("SELECT idx,url FROM entries"):
        idx, url = row
        print(idx)
        size = int(session.head(url).headers["Content-length"])
        assert size != 0
        print(size)
        conn.execute("UPDATE entries SET size = ? WHERE idx == ?", (size, idx))
        conn.commit()
