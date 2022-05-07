#!/usr/bin/env python
"""Generate podcast feed from database"""
import datetime
from logging import getLogger
from podgen import Podcast, Episode, Media, Person
from db import get_all_articles
from fetching import make_url_absolute


logger = getLogger(__name__)
__all__ = ["generate_feed"]


def generate_podcast_from_db() -> Podcast:
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
    for article in get_all_articles():
        assert article.summary.title.strip()
        for urlsize in article.medias:
            episode = Episode(
                title=article.summary.title,
                summary=article.summary.summary,
                authors=[Person(author) for author in article.summary.authors],
                image=make_url_absolute(article.image_url)
                if article.image_url
                else None,
                link=make_url_absolute(article.summary.url),
                media=Media(urlsize.url, urlsize.size),
                publication_date=datetime.datetime.combine(
                    article.summary.date, midnight
                ),
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
