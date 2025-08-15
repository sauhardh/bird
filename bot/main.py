from dotenv import load_dotenv
import requests

import logging
import json
import os
import sys
from pathlib import Path
import time
import random


from bot.core import Parser
from bot.core import Agent
from bot.core import DiscordWebhook
from .time import Clock
from bot.core import ImageDownload
from bot.core import Keyword
from bot.core import Overlay
from bot.core import Publish

logging.basicConfig(
    level=logging.INFO, format=" <%(name)s>   %(levelname)s => %(message)s "
)


class Bird:
    file_path: Path
    env_path: Path
    last_run_time: str | None
    discord: DiscordWebhook

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

            try:
                rephrased_list: list[dict] = Agent(api_key=_api_key).message(news_list)
            except (ConnectionError, OSError, requests.exceptions.ConnectionError) as e:
                logging.error(f"Network error {e}, SHUTTING DOWN!")
                self.discord.send_info(
                    "NETWORK ERROR",
                    "Shutting down, due to network error while requesting groq api",
                )
                sys.exit(1)

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

    def insert_entity(self, news_list: list[dict]):
        keyword = Keyword()

        for news in news_list:
            news["entity"] = keyword.extract_entities(news.get("rephrased_title", None))

    def download_image(self, news_list: list[dict]):
        image = ImageDownload()

        for news in news_list:
            entity = news.get("entity", None)
            if not entity:
                logging.warning(
                    f"FORMAT ERROR: no entity key found on dictionary for index {news.get('id', -1)}"
                )
                entity = news.get("title")
                self.discord.send_info(
                    "NO ENTITY FOUND",
                    f"for {news.get('rephrased_title', None)}, No entity has been found. Using `title` instead",
                )

            img_path = image.set_dest(entity).request()
            if img_path:
                news["img_path"] = img_path
            else:
                logging.warning(f"Did not get image path to append. for {entity}")

    def overlay_image(self, news_list: list[dict]):
        overlay = Overlay()

        for news in news_list:
            img_path = news.get("img_path", None)
            if img_path:
                if not overlay.find_img_to_draw(img_path):
                    logging.warning(f"No image found with this title: {img_path}")
                    continue

                txt = news.get("rephrased_title", news.get("title", None))
                if not txt:
                    logging.warning(
                        f"No title found to overlay for this img_path {img_path}"
                    )
                    continue

                overlay.load_font().text_overlay(txt)

    def post(self, news_list: list):
        publish = Publish()

        for news in news_list:
            time.sleep(random.choice([10, 12, 15, 11]))
            img_path = news.get("img_path", None)
            text = news.get("rephrased_summary")

            if not img_path:
                publish.post_text_only(text=text)
                logging.info(f"PUBLISHED-TWEET >>text only: {text}")
            else:
                publish.post_text_with_img(text=text, img_path=img_path)
                logging.info(f"PUBLISHED-TWEET >>image: {text}")

    def main(self):
        news_sites = self.load_news_site_url()

        news_collection = self.get_news_and_rephrase(news_sites)
        (rejected_news, accepted_news) = self.separate_news(news_collection)
        # sends this info to discord
        self.discord = DiscordWebhook().set_reject().send(rejected_news)
        # gives id to each news based on index
        accepted_news = self.insert_id(accepted_news)

        if len(accepted_news) <= 0:
            logging.info("EARLY EXIT: No new News Found.")
            self.discord.send_info("EARLY EXIT", f"No new News Found: {accepted_news}")
            sys.exit()

        duplicates: list = Agent().find_duplicate(news_list=accepted_news)
        duplicate_news = [
            news for news in accepted_news if news.get("id", -1) in duplicates
        ]
        accepted_news = [
            news for news in accepted_news if news.get("id", -1) not in duplicates
        ]

        self.discord.set_reject().send(duplicate_news).set_accept().send(accepted_news)
        # this updates `accepted_news` with `entity` key
        self.insert_entity(accepted_news)
        # this updates `accepted_news` with `img_path` key
        self.download_image(news_list=accepted_news)
        self.overlay_image(news_list=accepted_news)
        self.post(news_list=accepted_news)

        self.discord.send_info("COMPLETED", "Tweeting process completed")
        # saves the time
        Clock().save_time_log()
