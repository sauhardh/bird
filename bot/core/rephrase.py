from groq import Groq
from typing import Optional, List
import time
import logging

from bot.constants import MODEL, AI_CONTENT
from .content import Content


class RephraseAI:
    client = None
    model: None

    def __init__(self, api_key: str, model: Optional[str]):
        self.client = Groq()
        self.model = model if model else MODEL

    def message(self, news_list: dict) -> List:
        rephrased_news_list: List = []

        logging.info(
            "Sleeping for 10s before start. Just to cool down the rate limit (if any)"
        )
        time.sleep(10)
        for article in news_list:
            logging.info(
                "Sleeping for 3s before each article processing with AI. Just to cool down the rate limit (if any)"
            )
            time.sleep(3.0)

            more_content = Content(article["link"]).get_content()
            user_content = f"Title: {article['title']}, Summary: {article['summary']}, Article (sometime it may not match with title, if so ignore it): {more_content}. Give your Reply in this json format only {{viral_score: int (0 to 10), viral: bool, title: str, rephrased_title: str, rephrased_summary: str }}"

            messages = [
                {"role": "assistant", "content": AI_CONTENT},
                {"role": "user", "content": user_content},
            ]

            chat_completion = self.client.chat.completions.create(
                messages=messages, model=self.model
            )

            rephrased_news_list.append(chat_completion.choices[0].message.content)

        return rephrased_news_list
