import feedparser

import logging
from typing import TypedDict, Optional, List
from config.constants import NUMBER_OF_NEWS
from bot.time import Clock
from datetime import datetime


class NewsCollectionFormat(TypedDict):
    title: str
    summary: str
    link: str
    published: Optional[str]
    thumbnail: Optional[dict]


class Parser:
    """
    Parses essential data from an RSS (Really Simple Syndication) feed.

    This class/function extracts the latest news articles from a news website's RSS feed,
    which is typically provided in XML format. It returns a structured list of news items.

    Parameters:
        url (str): The URL of the RSS feed for a specific news website.

    Returns:
        List[dict]: A list of dictionaries, where each dictionary represents a news article with the following keys:
            - "title" (str): The headline of the article.
            - "summary" (str): A short summary or excerpt from the article.
            - "link" (str): The URL link to the full article.
            - "published" (str): The publication date and time of the article.
            - "thumbnail" (str): A URL to the article’s thumbnail image, if available.
    """

    url: str = None
    time_compare: bool = False
    clock: Clock
    last_run_time: str

    def __init__(self, url: str):
        self.url = url

    def compare_time(self, last_run_time: str | None):
        if last_run_time:
            self.last_run_time = last_run_time
            self.time_compare = True
            self.clock = Clock()
        else:
            self.time_compare = False

        return self

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
            published = entry.get("published", None)

            if self.time_compare and published:
                published: datetime | None = self.clock.convert_to_datetime(published)

                if published and (
                    not self.clock.compare_time(published, self.last_run_time)
                ):
                    logging.info(
                        f"SKIPPING!: This content is older({published}) than the last run time {self.last_run_time}."
                    )
                    continue

            news_obj: NewsCollectionFormat = {
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "link": entry.get("link", ""),
                "published": published,
                "thumbnail": entry.get("media_thumbnail", None)[0]
                if "media_thumbnail" in entry
                else None,
            }
            news_items.append(news_obj)

        return news_items
