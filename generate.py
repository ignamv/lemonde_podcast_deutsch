"""Generate podcast feed from database"""
import datetime
from logging import getLogger
from podgen import Podcast, Episode, Media, Person
from db import get_all_articles


logger = getLogger(__name__)
__all__ = ["generate_feed"]


def generate_podcast_from_db():
    """Create podgen.Podcast from database entries"""
    podcast = Podcast(
        name="Le Monde Diplomatique Deutsch",
        description=(
            "LE MONDE diplomatique, die große Monatszeitung für "
            "internationale Politik und Wirtschaft"
        ),
        website="https://monde-diplomatique.de",
        image="https://monde-diplomatique.de/images/logos/LE-MONDE-diplomatique-logo-short.png",
        language="de",
        explicit=False,
    )
    midnight = datetime.time(tzinfo=datetime.timezone.utc)
    for row in get_all_articles():
        if not row["title"]:
            continue
        episode = Episode(
            title=row["title"],
            summary=row["summary"],
            authors=[Person(author) for author in row["authors"]],
            image=row["image_url"],
            link=row["article_url"],
            media=Media(row["audio_url"], row["audio_size"]),
            publication_date=datetime.datetime.combine(row["date"], midnight),
        )
        podcast.episodes.append(episode)
    return podcast


def generate_feed():
    """Entry point"""
    podcast = generate_podcast_from_db()
    for name, minimize in (("debug", False), ("feed", True)):
        filename = f"output/{name}.xml"
        podcast.rss_file(filename, minimize=minimize)
        logger.info("Generated feed at %s", filename)


if __name__ == "__main__":
    generate_feed()
