from dotenv import load_dotenv

import logging
import json
import os
import sys
from pathlib import Path


from bot.core import Parser
from bot.core import Agent
from .discord import DiscordWebhook
from .time import Clock
from bot.core import Image
from bot.core import Keyword


logging.basicConfig(
    level=logging.INFO, format=" <%(name)s>   %(levelname)s => %(message)s "
)


class Bird:
    file_path: Path
    env_path: Path
    last_run_time: str | None

    def __init__(self):
        self.file_path = Path.cwd().joinpath("config").joinpath("news-site.json")
        self.env_path = Path.cwd().joinpath(".env")
        self.last_run_time = Clock().get_time_log()

    def load_news_site_url(self) -> dict[str, str]:
        """
        Reads the json file having list of RSS url of each news site at path `config/news-site.json`
        """
        file = open(self.file_path).read()
        return json.loads(file)

    def load_env_key(self) -> str | None:
        """
        Reads env key `GROQ_API_KEY` from path
        """
        load_dotenv(self.env_path)
        return os.getenv("GROQ_API_KEY")

    def insert_id(self, news_list: list[dict]) -> list[dict]:
        """
        This inserts `id` key on each dictionary. id starts from `0`
        """
        for id, news in enumerate(news_list):
            news["id"] = id

        return news_list

    def get_news_and_rephrase(self, news_sites: dict[str, str]) -> list[dict]:
        """
        Get the news from RSS feed and rephrase it using AI.
        uses `Parser` and `Agent` class
        """
        _api_key: str | None = self.load_env_key()

        news_collection: list[dict] = []

        for site in news_sites:
            news_list: list[dict] = (
                Parser(news_sites[site]).compare_time(self.last_run_time).parse()
            )
            rephrased_list: list[dict] = Agent().message(news_list)
            news_collection.extend(rephrased_list)

        return news_collection

    def separate_news(
        self, news_collection: list[dict]
    ) -> tuple[list[dict], list[dict]]:
        """
        This separate the news based on if it is `viral` and based on `viral_score`.
        if `viral` is `True` and    `viral_score` >= 7, post is accepted else rejected
        """
        rejected_news, accepted_news = [], []

        for news in news_collection:
            if news.get("viral", True) and news.get("viral_score", 8) >= 7:
                accepted_news.append(news)
            else:
                rejected_news.append(news)

        return (rejected_news, accepted_news)

    def insert_entity(self, news_list: list[dict]) -> list[dict]:
        keyword = Keyword()

        for news in news_list:
            news["entity"] = keyword.extract_entities(news.get("rephrased_title", None))

        return news_list

    def download_image(self, news_list):
        image = Image()

        for news in news_list:
            entity = news.get("entity", None)
            if not entity:
                logging.warning(
                    f"FORMAT ERROR: no entity key found on dictionary for index {news.get('id', -1)}"
                )
                continue

            image.set_header().set_dest(entity).set_brave_url().request()

    def main(self):
        news_sites = self.load_news_site_url()
        news_collection = self.get_news_and_rephrase(news_sites)

        (rejected_news, accepted_news) = self.separate_news(news_collection)

        # sends this info to discord
        discord = DiscordWebhook().set_reject().send(rejected_news)

        # gives id to each news based on index
        accepted_news = self.insert_id(accepted_news)

        if len(accepted_news) <= 0:
            logging.info("EARLY EXIT: No new News Found.")
            discord.set_info().send_info(
                "EARLY EXIT", f"No new News Found: {accepted_news}"
            )
            sys.exit()

        duplicates: list = Agent().find_duplicate(news_list=accepted_news)
        duplicate_news = [
            news for news in accepted_news if news.get("id", -1) in duplicates
        ]
        accepted_news = [
            news for news in accepted_news if news.get("id", -1) not in duplicates
        ]

        discord.set_reject().send(duplicate_news).set_accept().send(accepted_news)

        final_news_list: list[dict] = self.insert_entity(accepted_news)
        print("Final news list", final_news_list)

        self.download_image(news_list=final_news_list)
        # saves the time
        Clock().save_time_log()
