"""Generate podcast feed from database"""
import datetime
from logging import getLogger, basicConfig
from podgen import Podcast, Episode, Media
from db import get_db


logger = getLogger(__name__)


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
    for name, minimize in (('debug', False), ('feed', True)):
        filename = f"output/{name}.xml"
        podcast.rss_file(filename, minimize=False)
        logger.info('Generated feed at %s', filename)


if __name__ == "__main__":
    main()
