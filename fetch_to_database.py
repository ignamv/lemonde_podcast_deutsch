#!/usr/bin/env python
"""Fetch articles and save them to the database"""
import datetime
import logging
import re
from typing import Iterator, Tuple, List
from bs4 import BeautifulSoup
from lemondetypes import ArticleSummary, Article, UrlSize
from db import commit, get_last_downloaded_date, write_article_to_db
from fetching import fetch_issue_index, fetch_issue, fetch_article, get_url_size


logger = logging.getLogger(__name__)

__all__ = ["fetch_entries_to_database"]


def yield_archive_issues() -> Iterator[Tuple[datetime.date, str]]:
    """Yield (date, url) for all issues in text archive"""
    soup = BeautifulSoup(fetch_issue_index(), "html.parser")
    container = soup.find("section", class_="archiv jhrg")
    for link in container.find_all("a"):
        url = link.attrs["href"]
        match = re.match(r"/archiv-text\?text=(\d\d\d\d-\d\d-\d\d)", url)
        if not match:
            continue
        date = datetime.date.fromisoformat(match.group(1))
        yield date, url


def strip_prefix(string: str, prefix: str) -> str:
    """Remove prefix from string, if present"""
    if string.startswith(prefix):
        return string[len(prefix) :]
    return string


def fix_expand_author(dirty_authors: str) -> List[str]:
    """Clean up and separate authors"""
    # Some 'von's end up in the author names
    dirty_authors = strip_prefix(strip_prefix(dirty_authors.strip(), "von "), "Von ")
    if not dirty_authors:
        return []
    if " und " not in dirty_authors:
        return [dirty_authors]
    # Multiple authors got squashed together, separate
    authors = dirty_authors.split(", ")
    authors[-1:] = authors[-1].split(" und ")
    assert not any("," in author for author in authors)
    return [author.strip() for author in authors]


def parse_issue_html(html: str, date: datetime.date) -> Iterator[ArticleSummary]:
    """Yield ArticleSummary for all articles in issue html"""
    soup = BeautifulSoup(html, "html.parser")
    ul_tag = soup.find("ul", class_="inhaltsverz verlinkt")
    for li_tag in ul_tag.find_all("li"):
        mediasyncid = int(li_tag.attrs["mediasyncid"])
        divs = li_tag.find_all("div")
        titlediv = divs[0]
        summarydiv = divs[1]
        url = titlediv.find("a").attrs["href"]
        title = titlediv.find("strong").text
        summary = summarydiv.text
        authors = [em.text for em in li_tag.find_all("em")]
        if authors and authors[0].strip() == "von":
            authors = authors[1:]
        authors = [
            author for authors_ in authors for author in fix_expand_author(authors_)
        ]
        yield ArticleSummary(mediasyncid, url, title, date, summary, authors)


def test_parse_issue():
    """."""
    input_ = """
<ul class="inhaltsverz verlinkt">
  <li mediasyncid="5812125">
    <div>
      <a href="/artikel/!5812125"> <strong>the title</strong> </a>
    </div>
    <div>summary</div>
    <div>
      <span><em> von </em></span><span><em>author1</em></span>, <span><em>author2</em></span>
    </div>
  </li>
</ul>"""
    date = datetime.date(1998, 12, 30)
    (summary,) = parse_issue_html(input_, date)
    assert summary.mediasyncid == 5812125
    assert summary.url == "/artikel/!5812125"
    assert summary.title == "the title"
    assert summary.summary == "summary"
    assert summary.authors == ["author1", "author2"]
    assert summary.date == date


def parse_article(html: str) -> Tuple[str, str, List[str]]:
    """Return (title, image url, audio urls) from article html"""
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("title").text
    figure = soup.find("figure", role="group")
    imgurl = figure.find("img").attrs["src"] if figure is not None else None
    audiosection = soup.find("section", class_="audio feature")
    if audiosection is not None:
        mediaurls = [
            audio.attrs["src"] for audio in audiosection.find_all("audio", id="player2")
        ]
    else:
        mediaurls = []
    return title, imgurl, mediaurls


def yield_issue_articles(date: datetime.date, url: str) -> Iterator[Article]:
    """Yield articles for issue with given date and url"""
    article_summaries = parse_issue_html(fetch_issue(date, url), date)
    for article_summary in article_summaries:
        title, image_url, media_urls = parse_article(
            fetch_article(article_summary.mediasyncid, article_summary.url)
        )
        # If title was missing from the issue page, use the title from the article page
        if not article_summary.title.strip():
            article_summary.title = title
        medias = [UrlSize(url, get_url_size(url)) for url in media_urls]
        yield Article(article_summary, image_url, medias)


def fetch_entries_to_database():
    """Entry point"""
    last_downloaded_entry_date = get_last_downloaded_date()
    new_articles = 0
    first_date_with_audio = datetime.date(2011, 6, 10)
    for date, url in yield_archive_issues():
        if date < first_date_with_audio or (
            last_downloaded_entry_date is not None
            and date <= last_downloaded_entry_date
        ):
            continue
        logger.info("Found new issue %s", date)
        for article in yield_issue_articles(date, url):
            if not article.medias:
                continue
            write_article_to_db(article)
            new_articles += 1
    commit()
    return new_articles


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fetch_entries_to_database()
