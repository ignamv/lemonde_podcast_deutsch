# Listen to Le Monde Diplomatique (Deutsch) as podcast

![Tests](https://github.com/ignamv/lemonde_podcast_deutsch/actions/workflows/check.yml/badge.svg)

These scripts build an RSS feed for the [free audio archive of Le Monde Diplomatique](https://monde-diplomatique.de/archiv-audio).
You don't need to run them to listen to the podcast. Just point your podcast app to the [feed](https://ignamv.github.io/lemonde_podcast_deutsch/feed.xml).

# Code structure

HTTP requests are handled by `fetching.py`.
It implements rate limiting (to avoid loading the server).
It also caches responses to avoid repeated requests while experimenting.

Database access is handled by `db.py`.
I use an `sqlite3` database with tables `article`, `author` and `audiofile`.
The normalization is just for fun, I previously used a single table and that was more practical.

`fetch_entries_to_database.py` parses the issues index, issues and articles and saves everything to the database.

`generate_feed.py` reads the articles from the database and creates the RSS feed.

`upload_feed.py` does what it says on the tin.

`cronjob.py` executes the fetch, generate and upload scripts, skipping the latter if no new articles are available.
