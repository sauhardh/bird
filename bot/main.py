from dotenv import load_dotenv

import logging
from pathlib import Path
import json
import os
from typing import List

from bot.core import Parser
from bot.core import RephraseAI
from .discord import DiscordWebhook

logging.basicConfig(
    level=logging.INFO, format=" <%(name)s>   %(levelname)s => %(message)s "
)


def main():
    file_path = Path.cwd().joinpath("config").joinpath("news-site.json")
    file = open(file_path).read()
    news_sites = json.loads(file)

    env_path = Path.cwd().joinpath(".env")
    load_dotenv(env_path)
    api_key = os.getenv("GROQ_API_KEY")

    _news_collection: List = []
    for site in news_sites:
        news_list = Parser(news_sites[site]).parse()
        rephrased_list = RephraseAI(api_key, None).message(news_list)

        _news_collection.extend(rephrased_list)

    rejected_news = [
        x for x in _news_collection if not x["viral"] or x["viral_score"] < 7
    ]
    accepted_news = [
        x for x in _news_collection if x["viral"] and x["viral_score"] >= 7
    ]

    # sends this info to discord
    DiscordWebhook().set_reject().send(rejected_news).set_accept().send(accepted_news)

    print("rejected_news", rejected_news)
