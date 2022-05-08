CREATE TABLE article (
    mediasyncid INTEGER PRIMARY KEY,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    image_url TEXT,
    date DATE NOT NULL
);
CREATE INDEX article_date on article(date);
CREATE TABLE author (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);
CREATE INDEX author_name on author(name);
CREATE TABLE audiofile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mediasyncid INTEGER NOT NULL,
    url TEXT NOT NULL,
    size INTEGER NOT NULL,
    FOREIGN KEY(mediasyncid) REFERENCES article(mediasyncid)
);
CREATE TABLE "article_author" (
    mediasyncid INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    FOREIGN KEY(mediasyncid) REFERENCES article(mediasyncid),
    FOREIGN KEY(author_id) REFERENCES author(id),
    PRIMARY KEY(mediasyncid, author_id)
);
CREATE INDEX article_author__author on article_author(author_id);
CREATE TABLE sizecache (
    url TEXT PRIMARY KEY NOT NULL,
    size INTEGER NOT NULL
);
