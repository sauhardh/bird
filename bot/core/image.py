from bs4 import BeautifulSoup
import requests
import urllib.parse
import logging
from pathlib import Path
import random


class Image:
    headers: dict = None
    url: str = None
    max_req: int = 3
    dest_path: Path = None
    images_divs = None
    entity: str = None
    encoded_entity: str = None

    USER_AGENT = [
        # A few real browser UA strings
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    ]

    def set_dest_path(self, ext: str):
        file_name = "".join(self.entity.split(" "))
        dir_path = Path.cwd().joinpath("config").joinpath("imgs")
        dir_path.mkdir(exist_ok=True, parents=True)

        file_path = dir_path.joinpath(file_name + ext)
        print("cwd", file_path)
        self.dest_path = file_path

    def set_header(self):
        self.headers = {"User-Agent": random.choice(self.USER_AGENT)}

        return self

    def set_dest(self, entity: str):
        self.entity = entity
        self.encoded_entity = urllib.parse.quote_plus(string=entity)

        return self

    def set_brave_url(self):
        self.url = f"https://search.brave.com/images?q={self.encoded_entity}&source=web"

        return self

    def set_duckduckgo_url(self):
        self.url = (
            f"https://duckduckgo.com/?q={self.encoded_entity}&iax=images&ia=images"
        )

        return self

    def select_img(self, idx: int = 0) -> str | None:
        if not self.images_divs or idx >= len(self.images_divs):
            logging.warning(
                f"Index {idx} out of range for images_divs length {len(self.images_divs) if self.images_divs else 0}"
            )
            return None

        img_el = self.images_divs[idx].find("img")
        if img_el and img_el.has_attr("src"):
            return img_el.get("src")

        logging.warning(f"No <img> with src found at index {idx}")
        return None

    def request_img(
        self,
    ):
        for id in range(self.max_req):
            img_url = self.select_img(id)

            if img_url is None:
                logging.warning(
                    f"Failed to parse `src` attribute for index {id} out of {self.max_req}"
                )
                continue

            res = requests.get(img_url)
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
                    case _:  # default: "image/jpeg"
                        ext = ".jpg"

                self.set_dest_path(ext=ext)

                with open(self.dest_path, "wb") as f:
                    f.write(res.content)
                    logging.info(
                        f"Successfully downloaded image. Find it here: {self.dest_path}"
                    )
                break

    def request(self):
        if not self.headers or not self.url:
            logging.warning(
                "Failed to get header or url. Please call `set_url` or `set_header` beforehand"
            )
            return None

        try:
            res = requests.get(url=self.url, headers=self.headers)
        except Exception as e:
            pass

        if res.status_code not in (200, 201):
            logging.warning(
                "Unexpected result on searching image. Code:", res.status_code
            )
            return None

        soup = BeautifulSoup(res.text, "html.parser")
        self.images_divs = soup.find_all(class_="image-result")

        if len(self.images_divs) <= self.max_req:
            self.max_req = len(self.images_divs)

        self.request_img()
