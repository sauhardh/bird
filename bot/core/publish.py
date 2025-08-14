import tweepy
from tweepy.api import API
from dotenv import load_dotenv
import tweepy.errors

from os import getenv
import logging
from pathlib import Path
import time
import datetime

from .discord import DiscordWebhook
from config.constants import X_CHARACTER_LIMIT


class Publish:
    v1_api: API
    v2_client: tweepy.Client
    discord = DiscordWebhook()
    NUM_OF_RETRY = 3

    def __init__(self):
        load_dotenv()
        consumer_key = getenv("X_API_KEY")
        consumer_secret = getenv("X_API_KEY_SECRET")
        access_token = getenv("X_ACCESS_TOKEN")
        access_token_secret = getenv("X_ACCESS_TOKEN_SECRET")

        self.v2_client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )

        auth = tweepy.OAuth1UserHandler(
            consumer_key, consumer_secret, access_token, access_token_secret
        )
        self.v1_api = tweepy.API(auth)

    def __get_tweets(self, text: str) -> list:
        replies: list[str] = []

        if len(text) > X_CHARACTER_LIMIT:
            words = text.split()
            line = ""
            for word in words:
                if len(line) + len(word) + (1 if line else 0) <= X_CHARACTER_LIMIT:
                    line = f"{line} {word}".strip()
                else:
                    replies.append(line)
                    line = word
            if line:
                replies.append(line)
        else:
            replies.append(text)

        return replies

    def _reply_with_text(self, reply: str, tweet_id: str):
        RETRY = self.NUM_OF_RETRY
        while RETRY > 0:
            try:
                time.sleep(10)  # delay 10s before reply
                RETRY -= 1
                res = self.v2_client.create_tweet(
                    text=reply, in_reply_to_tweet_id=tweet_id
                )
                if res.data:
                    reply_id = res.data.get("id", None)
                    logging.info(
                        f"SUCCESS REPLY: For tweet {tweet_id}. replied successfully with id: {reply_id}"
                    )
                else:
                    logging.warning(f"Failed to reply a tweet with id {reply_id}.")
                break

            except tweepy.errors.TooManyRequests as e:
                reset_time = int(
                    e.response.headers.get("x-rate-limit-reset", time.time() + 900)
                )
                wait_sec = max(0, reset_time - time.time())
                readable_format = datetime.datetime.fromtimestamp(reset_time)

                logging.warning(
                    f"Rate limit hit on upload. Reset at {readable_format} <{wait_sec}> seconds away."
                )
                self.discord.send_info(
                    "RATE LIMIT HIT (media upload)",
                    f"Reset at `{readable_format}`. <{wait_sec}> seconds away.",
                )
                if wait_sec < 300:
                    time.sleep(wait_sec)
                else:
                    return

            except Exception as e:
                logging.warning(f"Unexpected error replying to tweet. {e}")
                break

    def post_text_only(self, text: str, media_id: str | None = None):
        replies: list = self.__get_tweets(text)
        if not replies:
            logging.warning(f"Nothing to tweet. Empty text: {text}, replies: {replies}")
            return

        RETRY = self.NUM_OF_RETRY
        while RETRY > 0:
            try:
                RETRY -= 1
                res = self.v2_client.create_tweet(
                    text=replies[0], media_ids=[media_id] if media_id else None
                )

                if not res.data:
                    logging.warning(f"Failed to tweet. {res}")
                    return

                tweet_id = res.data.get("id", None)
                logging.info("Tweeted successfully!")
                replies.pop(0)
                break
            except tweepy.errors.TooManyRequests as e:
                reset_time = int(
                    e.response.headers.get("x-rate-limit-reset", time.time() + 900)
                )
                wait_sec = max(0, reset_time - time.time())
                readable_format = datetime.datetime.fromtimestamp(reset_time)

                logging.warning(
                    f"Rate limit hit on upload. Reset at {readable_format} <{wait_sec}> seconds away."
                )
                self.discord.send_info(
                    "RATE LIMIT HIT (media upload)",
                    f"Reset at `{readable_format}`. <{wait_sec}> seconds away.",
                )
                if wait_sec < 300:
                    time.sleep(wait_sec)
                else:
                    return

            except Exception as e:
                logging.warning(f"Unexpected error occured {e}")
                return
        # replies
        for reply in replies:
            if not tweet_id:
                logging.warning("Failed to parse tweet_id. Skipping!")
                continue
            self._reply_with_text(reply, tweet_id)

    def post_text_with_img(self, text: str, img_path: str):
        img_path = Path(img_path)
        media_id = None

        # upload media
        RETRY = self.NUM_OF_RETRY
        while RETRY > 0:
            try:
                RETRY -= 1
                media = self.v1_api.media_upload(img_path)
                media_id = media.media_id
                break

            except tweepy.errors.TooManyRequests as e:
                reset_time = int(
                    e.response.headers.get("x-rate-limit-reset", time.time() + 900)
                )
                wait_sec = max(0, reset_time - time.time())
                readable_format = datetime.datetime.fromtimestamp(reset_time)

                logging.warning(
                    f"Rate limit hit on upload. Reset at {readable_format} <{wait_sec}> seconds away."
                )
                self.discord.send_info(
                    "RATE LIMIT HIT (media upload)",
                    f"Reset at `{readable_format}`. <{wait_sec}> seconds away.",
                )

                if wait_sec < 300:
                    time.sleep(wait_sec)
                else:
                    return

        if not media_id:
            logging.warning(f"Failed to parse media_id. {media_id}")
            return

        # create_tweet_with_potential_reply
        self.post_text_only(text, media_id)


if __name__ == "__main__":
    path = Path.cwd().joinpath("config").joinpath("imgs").joinpath("trumpukraine.jpg")

    Publish().post_text_with_img(
        text="The sun sets slowly behind the mountain, casting a warm golden glow over the serene valley, where wildflowers bloom in vibrant hues and gentle breezes whisper through ancient trees, their leaves rustling softly in harmony with the songs of distant birds. A clear stream meanders through the lush meadow, reflecting the fading light of dusk in its tranquil waters, inviting weary travelers to pause and marvel at nature’s timeless beauty, a fleeting moment of peace in a world that often moves too fast.",
        img_path=path,
    )
