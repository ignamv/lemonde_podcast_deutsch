"""Dataclasses"""
from dataclasses import dataclass
import datetime
from typing import List


@dataclass
class ArticleSummary:
    """Article metadata found in issue page"""

    mediasyncid: int
    url: str
    title: str
    date: datetime.date
    summary: str
    authors: List[str]


@dataclass
class UrlSize:
    """Url and size in bytes"""

    url: str
    size: int


@dataclass
class Article:
    """Article content found in article page"""

    summary: ArticleSummary
    image_url: str
    medias: List[UrlSize]
