#!/usr/bin/env python
"""Fetch articles and save them to the database"""
import datetime
import logging
import re
from bs4 import BeautifulSoup
from db import commit, get_last_downloaded_date, write_media_to_db
from fetching import fetch_issue_index, fetch_issue, fetch_article, get_url_size


logger = logging.getLogger(__name__)

__all__ = ["fetch_entries_to_database"]


def yield_archive_issues():
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


def parse_issue_html(html):
    """Yield (id, url, title, summary, authors) for all articles in issue html"""
    soup = BeautifulSoup(html, "html.parser")
    ul_tag = soup.find("ul", class_="inhaltsverz verlinkt")
    for li_tag in ul_tag.find_all("li"):
        id_ = int(li_tag.attrs["mediasyncid"])
        divs = li_tag.find_all("div")
        titlediv = divs[0]
        summarydiv = divs[1]
        url = titlediv.find("a").attrs["href"]
        title = titlediv.find("strong").text
        summary = summarydiv.text
        authors = [em.text for em in li_tag.find_all("em")]
        if authors and authors[0].strip() == "von":
            authors = authors[1:]
        yield id_, url, title, summary, authors


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
    ((id_, url, title, summary, authors),) = parse_issue_html(input_)
    assert id_ == 5812125
    assert url == "/artikel/!5812125"
    assert title == "the title"
    assert summary == "summary"
    assert authors == ["author1", "author2"]


def parse_article(html):
    """Return (image url, audio urls) from article html"""
    soup = BeautifulSoup(html, "html.parser")
    figure = soup.find("figure", role="group")
    imgurl = figure.find("img").attrs["src"] if figure is not None else None
    audiosection = soup.find("section", class_="audio feature")
    if audiosection is not None:
        mediaurls = [
            audio.attrs["src"] for audio in audiosection.find_all("audio", id="player2")
        ]
    else:
        mediaurls = []
    return imgurl, mediaurls


def yield_issue_articles(date, url):
    """Yield articles for issue with given date and url"""
    article_summaries = parse_issue_html(fetch_issue(date, url))
    for article_summary in article_summaries:
        id_, url, title, summary, authors = article_summary
        imgurl, mediaurls = parse_article(fetch_article(id_, url))
        mediaurls = [(url, get_url_size(url)) for url in mediaurls]
        yield {
            "original_index": id_,
            "date": date,
            "article_url": url,
            "title": title,
            "summary": summary,
            "authors": authors,
            "image_url": imgurl,
            "mediaurls": mediaurls,
        }


def write_article_to_db(article):
    """Write an entry to database for each media url in article"""
    for audio_url, audio_size in article["mediaurls"]:
        entry = {k: v for k, v in article.items() if k != "mediaurls"}
        entry.update(audio_url=audio_url, audio_size=audio_size)
        write_media_to_db(entry)


def fetch_entries_to_database():
    """Entry point"""
    last_downloaded_entry_date = get_last_downloaded_date()
    new_articles = 0
    for date, url in yield_archive_issues():
        if date <= last_downloaded_entry_date:
            continue
        logger.info("Found new issue %s", date)
        for article in yield_issue_articles(date, url):
            write_article_to_db(article)
            new_articles += 1
    commit()
    return new_articles


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fetch_entries_to_database()
