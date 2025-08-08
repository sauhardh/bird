from dotenv import load_dotenv

import logging
from pathlib import Path
import json
import os
from typing import List, Tuple
import sys


from bot.core import Parser
from bot.core import RephraseAI
from .discord import DiscordWebhook
from .time import Clock


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

    def insert_id(self, news_list: List[dict]) -> List[dict]:
        """
        This inserts `id` key on each dictionary. id starts from `1`
        """
        for id, news in enumerate(news_list):
            news["id"] = id + 1

        return news_list

    def get_news_and_rephrase(self, news_sites: dict[str, str]) -> List[dict]:
        """
        Get the news from RSS feed and rephrase it using AI.
        uses `Parser` and `RephraseAI` class
        """
        _api_key: str | None = self.load_env_key()

        news_collection: List[dict] = []

        for site in news_sites:
            news_list: List[dict] = (
                Parser(news_sites[site]).compare_time(self.last_run_time).parse()
            )
            rephrased_list: List[dict] = RephraseAI(None).message(news_list)
            news_collection.extend(rephrased_list)

        return news_collection

    def separate_news(
        self, news_collection: List[dict]
    ) -> Tuple[List[dict], List[dict]]:
        """
        This separate the news based on if it is `viral` and based on `viral_score`.
        if `viral` is `True` and    `viral_score` >= 7, post is accepted else rejected
        """
        rejected_news, accepted_news = [], []

        for news in news_collection:
            if news["viral"] and news["viral_score"] >= 7:
                accepted_news.append(news)
            else:
                rejected_news.append(news)

        return (rejected_news, accepted_news)

    def main(self):
        news_sites = self.load_news_site_url()
        news_collection = self.get_news_and_rephrase(news_sites)

        (rejected_news, accepted_news) = self.separate_news(news_collection)

        # sends this info to discord
        discord = (
            DiscordWebhook()
            .set_reject()
            .send(rejected_news)
            .set_accept()
            .send(accepted_news)
        )

        # gives id to each news based on index
        accepted_news = self.insert_id(accepted_news)

        print("accepted news", accepted_news)

        if len(accepted_news) <= 0:
            logging.info("EARLY EXIT: No New news Found.")
            discord.set_info().send_info(
                "EARLY EXIT", f"No new News Found: {accepted_news}"
            )
            sys.exit()

        for id, each_news in enumerate(accepted_news):
            pass

        # saves the time
        Clock().save_time_log()
