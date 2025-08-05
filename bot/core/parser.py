import feedparser
import logging


class Parser:
    url: str = None

    def __init__(self, url: str):
        self.url = url

    def parse(self):
        if self.url is None:
            logging.error(
                "url field is None. Please call '__init__()' first and pass the url"
            )
            return

        feed = feedparser.parse(self.url)

        for entry in feed.entries[:5]:
            print("entry:", entry)
