import feedparser

import logging
from typing import TypedDict, Optional, List
from bot.constants import NUMBER_OF_NEWS


class NewsCollectionFormat(TypedDict):
    title: str
    summary: str
    link: str
    published: Optional[str]
    thumbnail: Optional[dict]


class Parser:
    url: str = None

    def __init__(self, url: str):
        self.url = url

    def parse(self) -> List:
        if self.url is None:
            logging.error(
                "url field is None. Please call '__init__()' first and pass the url"
            )
            return

        feed = feedparser.parse(self.url)
        entry_len = min(NUMBER_OF_NEWS, len(feed.entries))

        news_items: List[NewsCollectionFormat] = []

        for entry in feed.entries[:entry_len]:
            news_obj: NewsCollectionFormat = {
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", None),
                "thumbnail": entry.get("media_thumbnail", None)[0]
                if "media_thumbnail" in entry
                else None,
            }
            news_items.append(news_obj)

        return news_items
