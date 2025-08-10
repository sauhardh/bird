from bs4 import BeautifulSoup
import requests
import urllib.parse
import logging
from pathlib import Path
import random
import time
from duckduckgo_search import DDGS


class Image:
    url: str = None
    max_req: int = 3
    dest_path: Path = None
    entity: str = None
    encoded_entity: str = None
    imgs: list = None
    url_flag: str = None

    USER_AGENT = [
        # A few real browser UA strings
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": random.choice(self.USER_AGENT),
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://search.brave.com/",
                "Connection": "keep-alive",
            }
        )

    def set_dest_path(self, ext: str):
        file_name = "".join(self.entity.split(" "))
        dir_path = Path.cwd().joinpath("config").joinpath("imgs")
        dir_path.mkdir(exist_ok=True, parents=True)

        file_path = dir_path.joinpath(file_name + ext)
        print("cwd", file_path)
        self.dest_path = file_path

    def set_dest(self, entity: str):
        self.entity = entity
        self.encoded_entity = urllib.parse.quote_plus(string=entity)

        return self

    def set_brave_url(self):
        self.url_flag = "brave"
        self.url = f"https://search.brave.com/images?q={self.encoded_entity}&source=web"

        return self

    def set_duckduckgo_url(self):
        self.url_flag = "duck"
        self.url = (
            f"https://duckduckgo.com/?q={self.encoded_entity}&iax=images&ia=images"
        )

        return self

    def select_img(self, idx: int = 0) -> str | None:
        if not self.imgs or idx >= len(self.imgs):
            logging.warning(
                f"Index {idx} out of range for images_divs length {len(self.imgs) if self.imgs else 0}"
            )
            return None

        return self.imgs[idx]

    def request_img(
        self,
    ) -> bool:
        for id in range(self.max_req):
            img_url = self.select_img(id)

            if img_url is None:
                logging.warning(
                    f"Failed to parse `src` attribute for index {id} out of {self.max_req}"
                )
                continue

            time.sleep(random.choice([3.1, 3.5, 4.7, 4.2]))
            try:
                res = self.session.get(img_url, timeout=10)
            except Exception as e:
                logging.warning("Error on downloading image from url %s", e)
                continue

            if res.status_code not in (200, 2001):
                logging.warning(
                    f"Failed to get image url for index {id} out of {self.max_req}"
                )
                continue
            else:
                ext: str
                content_type = res.headers.get("Content-Type")
                match content_type:
                    case "image/png":
                        ext = ".png"
                    case "image/gif":
                        ext = ".gif"
                    case "image/webp":
                        ext = ".webp"
                    case _:  # default: "image/jpeg"
                        ext = ".jpg"

                self.set_dest_path(ext=ext)

                with open(self.dest_path, "wb") as f:
                    f.write(res.content)
                    logging.info(
                        f"Successfully downloaded image. Find it here: {self.dest_path}"
                    )
                    return True
        return False

    def request(self) -> bool:
        try:
            self.set_duckduckgo_url()
            res: dict = DDGS().images(self.entity, max_results=10)
            imgs = [r["image"] or r["thumbnail"] for r in res if isinstance(r, dict)]
        except Exception as duck_e:
            logging.warning(
                "Error occured on requesting from duckduckgo search %s", duck_e
            )

            try:
                self.set_brave_url()
                res = self.session.get(self.url, timeout=10)
            except Exception as brave_e:
                logging.warning(
                    "Error occured on requesting from brave search %s",
                    brave_e,
                )
                return False

        if self.url_flag == "brave":
            soup = BeautifulSoup(res.text, "html.parser")

            imgs = [
                img["src"]
                for img in soup.find_all("img")
                if img.get("src")
                and img["src"].startswith("http")
                and "brave-logo" not in img["src"]
                and "rs:fit:32:32:1:0" not in img["src"]
                and "rs:fit:0:180:1:0" not in img["src"]
            ]

        self.imgs = imgs
        logging.info("Images are %s", imgs)

        if not self.imgs:
            logging.warning("No valid images found for query: %s", self.entity)
            return False

        self.max_req = min(self.max_req, len(self.imgs))

        return self.request_img()
