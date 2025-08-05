# read the config file
# call other functionality

import logging
from pathlib import Path
import json

from bot.core import Parser

logging.basicConfig(
    level=logging.INFO, format=" %(name)s | %(levelname)s => %(message)s"
)


def main():
    file_path = Path.cwd().joinpath("config").joinpath("news-site.json")
    file = open(file_path).read()
    obj = json.loads(file)

    print("url: ", obj["1"])
    Parser(obj["1"]).parse()
    # for x in obj:
    #     print("url", obj[x])

    print("f", file_path)
    pass
