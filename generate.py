"""Generate podcast feed from database"""
import datetime
from podgen import Podcast, Episode, Media
from db import get_db


def generate_podcast_from_db():
    """Create podgen.Podcast from database entries"""
    podcast = Podcast(
        name="Le Monde Diplomatique Deutsch",
        description=(
            "LMd auf die Ohren: In unserem Audioarchiv können Sie sich alle Ausgaben "
            "der Zeitung seit Juni 2011 vorlesen lassen."
        ),
        website="https://monde-diplomatique.de",
        explicit=False,
    )
    midnight = datetime.time(tzinfo=datetime.timezone.utc)
    with get_db() as conn:
        for row in conn.execute(
            "SELECT date, title, url, size FROM entries ORDER BY date DESC"
        ):
            episode = Episode(
                title=row["title"],
                media=Media(row["url"], row["size"]),
                publication_date=datetime.datetime.combine(row["date"], midnight),
            )
            podcast.episodes.append(episode)
    return podcast


def main():
    """Entry point"""
    podcast = generate_podcast_from_db()
    podcast.rss_file("output/debug.xml", minimize=False)
    podcast.rss_file("output/feed.xml", minimize=True)


if __name__ == "__main__":
    main()
