CREATE TABLE article (
    mediasyncid INTEGER PRIMARY KEY,
    url TEXT,
    title TEXT,
    summary TEXT,
    image_url TEXT,
    date DATE
);
CREATE INDEX article_date on article(date);
CREATE TABLE author (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
);
CREATE INDEX author_name on author(name);
CREATE TABLE audiofile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mediasyncid INTEGER,
    url TEXT,
    size INTEGER,
    FOREIGN KEY(mediasyncid) REFERENCES article(mediasyncid)
);
CREATE TABLE "article_author" (
    mediasyncid INTEGER,
    author_id INTEGER,
    FOREIGN KEY(mediasyncid) REFERENCES article(mediasyncid),
    FOREIGN KEY(author_id) REFERENCES author(id),
    PRIMARY KEY(mediasyncid, author_id)
);
CREATE INDEX article_author__author on article_author(author_id);
CREATE TABLE sizecache (
    url TEXT PRIMARY KEY,
    size INTEGER
);
