from groq import Groq
from typing import Optional, List
import time
import logging
import re
import json

from config.constants import MODEL, AI_CONTENT
from .content import Content


class RephraseAI:
    client = None
    model: None

    def __init__(self, _api_key: str, model: Optional[str]):
        # This automatically infers the api_key argument from the GROQ_API_KEY environment variable if it is not provided.
        self.client = Groq(api_key=_api_key)
        self.model = model if model else MODEL

    def message(self, news_list: dict) -> List:
        rephrased_news_list: List = []

        logging.info(
            "Sleeping for 30s before start. Just to cool down the rate limit (if any)"
        )
        time.sleep(3)

        for article in news_list:
            logging.info(
                "Sleeping for 10s before requesting to API. Just to cool down the rate limit (if any)"
            )
            time.sleep(1)

            more_content = Content(article["link"]).get_content()
            user_content = f"""
            You are evaluating a news article for its viral potential.

            Here is the information:
            - Title: {article["title"]}
            - Summary: {article["summary"]}
            - Full Article Content (sometimes may not match title/summary — if so, ignore article content): {more_content}

            🎯 Your task:
            1. Decide if this news has **high viral potential** (true/false).
            2. Rephrase the title and summary to make them:
            - Short
            - Attention-grabbing
            - Clear
            - Suitable for social media sharing
            3. Score the **viral potential** from 0 to 10 based on:
            - Public interest
            - Relevance to trending topics
            - Involvement of celebrities, politics, scandals, or surprising developments

            📌 Only reply with a JSON object in **this exact format**:

            {{
            "viral_score": 0-10,
            "viral": true/false,
            "title": "...",  // original
            "rephrased_title": "...", 
            "rephrased_summary": "..."
            }}
            
            """

            messages = [
                {"role": "assistant", "content": AI_CONTENT},
                {"role": "user", "content": user_content},
            ]

            chat_completion = self.client.chat.completions.create(
                messages=messages, model=self.model
            )

            string_content = chat_completion.choices[0].message.content

            start_idx = string_content.find("{")
            string_content = string_content[start_idx:]

            end_idx = string_content.find("}")
            string_content = string_content[: (end_idx + 1)]

            try:
                data = json.loads(string_content)
                string_content = data

            except json.JSONDecodeError as e:
                logging.error("JSON decode error", e)
                return None

            rephrased_news_list.append(string_content)

        return rephrased_news_list
