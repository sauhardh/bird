from bs4 import BeautifulSoup
import requests
from ddgs import DDGS
from PIL import Image, ImageFont, ImageDraw
from PIL.Image import Image as PILImage
from PIL.ImageDraw import ImageDraw as PILImageDraw

import urllib.parse
import logging
from pathlib import Path
import random
import time

from config.constants import CENSOR_WORDS


class ImageDownload:
    url: str = None
    max_req: int = 3
    dest_path: Path = None
    entity: str = None
    encoded_entity: str = None
    imgs: list = None
    url_flag: str = None

    USER_AGENT = [
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

    def __set_dest_path(self, ext: str):
        file_name = "".join(self.entity.split(" "))
        dir_path = Path.cwd().joinpath("config").joinpath("imgs")
        dir_path.mkdir(exist_ok=True, parents=True)

        file_path = dir_path.joinpath(file_name + ext)
        self.dest_path = file_path

    def set_dest(self, entity: str):
        self.entity = entity
        self.encoded_entity = urllib.parse.quote_plus(string=entity)
        return self

    def set_brave_url(self):
        self.url_flag = "brave"
        self.url = f"https://search.brave.com/images?q={self.encoded_entity}&source=web"
        return self

    # def set_duckduckgo_url(self):
    #     self.url_flag = "duck"
    #     self.url = (
    #         f"https://duckduckgo.com/?q={self.encoded_entity}&iax=images&ia=images"
    #     )
    #     return self

    def __select_img(self, idx: int = 0) -> str | None:
        if not self.imgs or idx >= len(self.imgs):
            logging.warning(
                f"Index {idx} out of range for images_divs length {len(self.imgs) if self.imgs else 0}"
            )
            return None
        return self.imgs[idx]

    def _request_img(
        self,
    ) -> bool:
        for id in range(self.max_req):
            img_url = self.__select_img(id)

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

                self.__set_dest_path(ext=ext)
                with open(self.dest_path, "wb") as f:
                    f.write(res.content)
                    logging.info(
                        f"Successfully downloaded image. Find it here: {self.dest_path}"
                    )
                    return True
        return False

    def request(self) -> str | None:
        try:
            # self.set_duckduckgo_url()
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
                _img["src"]
                for _img in soup.find_all("_img")
                if _img.get("src")
                and _img["src"].startswith("http")
                and "brave-logo" not in _img["src"]
                and "rs:fit:32:32:1:0" not in _img["src"]
                and "rs:fit:0:180:1:0" not in _img["src"]
            ]

        self.imgs = imgs
        logging.info("Images are %s", imgs)

        if not self.imgs:
            logging.warning("No valid images found for query: %s", self.entity)
            return False

        self.max_req = min(self.max_req, len(self.imgs))

        if self._request_img():
            return self.dest_path
        else:
            return None


# --------------------#
#       OVERLAY       #
# --------------------#


class Overlay:
    """
    This overlay text on the image like a thumbnail
    """

    path: Path
    _img: PILImage
    img_path: Path
    txt: str

    def __init__(self):
        self.path = Path.cwd().joinpath("config")

    def find_img_to_draw(self, img_path: str) -> bool:
        self.img_path = Path(img_path)

        if not self.img_path.exists():
            logging.warning(
                f"No directory or image of such exists. __Path lookup__: {self.img_path}"
            )
            return False

        try:
            self._img = Image.open(self.img_path).convert("RGBA")
        except Exception as e:
            logging.warning(f"Failed to open the image on path {self.img_path}")
            return False

        return True

    def load_font(self):
        try:
            if not self._img:
                logging.warning(
                    "No image found. Please call `find_img_to_draw()` beforehand"
                )

            self.font = ImageFont.truetype(
                self.path.joinpath("Roboto-Medium.ttf"),
                size=int(self._img.height * 0.095),
            )
        except OSError:
            self.font = ImageFont.load_default()
        return self

    def _wrap_text(self, draw: PILImageDraw, max_width: int) -> list:
        lines = []
        words = self.txt.split(" ")
        line = ""

        for word in words:
            if any(
                word.lower().startswith(censor_word) for censor_word in CENSOR_WORDS
            ):
                letters = list(word)
                letters.insert(1, "*")
                word = "".join(letters)

            test_line = f"{line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=self.font)
            line_w = bbox[2] - bbox[0]

            if line_w <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)

        return lines

    def text_overlay(self, txt: str):
        padding = 20
        max_width = self._img.width - padding
        self.txt = txt

        overlay = Image.new("RGBA", self._img.size, (255, 255, 255, 0))
        draw: PILImageDraw = ImageDraw.Draw(overlay)

        lines: list = self._wrap_text(draw, max_width)
        line_height = self.font.getbbox("Ay")[3] - self.font.getbbox("Ay")[1]
        total_height = line_height * len(lines) + (len(lines) - 1) * 10
        # position to start text on y axis
        y = self._img.height - total_height - (padding * 2)

        for idx, line in enumerate(lines):
            bbox = draw.textbbox(
                (
                    0,
                    0,
                ),
                line,
                font=self.font,
            )

            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            x = (self._img.width - text_w) / 2

            # semi-transparent-background
            bg_padding_x = 10
            bg_padding_y = 5
            draw.rectangle(
                [
                    x - bg_padding_x,
                    y - bg_padding_y,
                    x + text_w + bg_padding_x,
                    y + text_h + (bg_padding_y * 3),
                ],
                fill=(0, 0, 0, 170),
            )

            draw.text((x, y), line, font=self.font, fill="white")
            y += line_height + (bg_padding_y * 2) + 1

        merged = Image.alpha_composite(self._img, overlay)
        merged.convert("RGB").save(self.img_path, quality=90)
        logging.info(f"Thumbnail saved: {self.img_path}")
