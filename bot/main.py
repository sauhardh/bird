# read the config file
# call other functionality

from dotenv import load_dotenv

import logging
from pathlib import Path
import json
import os

from bot.core import Parser
from bot.core import RephraseAI
from bot.core import Content

logging.basicConfig(
    level=logging.INFO, format=" %(name)s | %(levelname)s => %(message)s"
)


def main():
    file_path = Path.cwd().joinpath("config").joinpath("news-site.json")
    file = open(file_path).read()
    news_sites = json.loads(file)

    env_path = Path.cwd().joinpath(".env")
    load_dotenv(env_path)

    api_key = os.getenv("GROQ_API_KEY")

    for site in news_sites:
        print("site", site)
        l = Parser(news_sites[site]).parse()
        # print("l", l)

        r = RephraseAI(api_key, None).message(l)

        print("list for", site, "_____", r)
