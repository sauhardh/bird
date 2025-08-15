from groq import Groq
import groq
import time
import logging
import json
import ast

from config.constants import MODEL, AI_CONTENT_REPHRASE, AI_CONTENT_FILTER
from .content import Content
from .discord import DiscordWebhook


class Agent:
    client: Groq
    model: str

    def __init__(self, model: str = MODEL):
        # This automatically infers the api_key argument from the GROQ_API_KEY environment variable if it is not provided.
        self.client = Groq()
        self.model = model

    def message(self, news_list: dict) -> list:
        rephrased_news_list: list = []

        logging.info(
            "Sleeping for 30s before start. Just to cool down the rate limit (if any)"
        )
        time.sleep(3)

        for article in news_list:
            logging.info(
                "Sleeping for 10s before requesting to API. Just to cool down the rate limit (if any)"
            )
            time.sleep(1)

            more_content: str = Content(article["link"]).get_content()
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
            - Summary: rewrite it in a casual, human-like tone — as if a person is reacting to the news on X (Twitter).
                Can include light emotion, urgency, or opinion (without adding false facts).
                Should feel natural, like a real user posting about it. You can put related emoji on it.
            - Respond with ONLY valid JSON, Double check if necessary but do not include extra text.

            3. Score the **viral potential** from 0 to 10 based on:
            - Public interest
            - Relevance to trending topics
            - Involvement of celebrities, politics, scandals, or surprising developments

            📌 Only reply with a JSON object in **this exact format**:

            ```
            {{
            "viral_score": 0-10, 
            "viral": true/false,
            "title": "...", 
            "rephrased_title": "...", 
            "rephrased_summary": "..."
            }}
            ```

            """

            messages = [
                {"role": "assistant", "content": AI_CONTENT_REPHRASE},
                {"role": "user", "content": user_content},
            ]

            chat_completion = self.client.chat.completions.create(
                messages=messages, model=self.model
            )

            string_content = chat_completion.choices[0].message.content

            if not string_content:
                logging.warning(f"No response for article: {article['title']}")
                continue

            start_idx = string_content.find("{")
            string_content = string_content[start_idx:]

            end_idx = string_content.find("}")
            string_content = string_content[: (end_idx + 1)]

            try:
                data = json.loads(string_content)
                string_content = data

            except json.JSONDecodeError as e:
                logging.error(
                    f"JSON decode error. Failed to parse the json. for {string_content} ",
                    e,
                )
                DiscordWebhook().send_info(
                    "JSON DECODE ERROR",
                    f"SKIPPING: Failed to parse the json for {string_content}",
                )
                continue

            string_content["link"] = article.get("link", None)
            string_content["published"] = article.get("published", None)
            string_content["thumbnail"] = article.get("thumbnail", None)

            rephrased_news_list.append(string_content)

        return rephrased_news_list

    def find_duplicate(self, news_list: dict) -> list:
        formatted_news_list: list[dict] = [
            {news.get("id", -1): news.get("rephrased_summary", "")}
            for news in news_list
        ]

        formatted_news_json = json.dumps(
            formatted_news_list, ensure_ascii=False, indent=2
        )

        user_content: str = f"""
        Here is a JSON list of news items:

        {formatted_news_json}

        Task:
        - Identify duplicate news items based on their summaries following your rules.
        - Return ONLY the JSON list of duplicate IDs to remove, nothing else.
        - If there are no duplicates, return [] exactly.
        - Critical: Do not add extra any information or explanation, **no nothing extra**.


        📌 Only reply with a JSON object in **this exact format**:
        ```
        []
        ```
        """

        messages = [
            {"role": "assistant", "content": AI_CONTENT_FILTER},
            {"role": "user", "content": user_content},
        ]

        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages, model=self.model
            )
        except groq.APIConnectionError as e:
            logging.warning(
                f"Skipping article due to connection error: {chat_completion} | {e}"
            )
            return []

        string_content: str = chat_completion.choices[0].message.content

        start_idx = string_content.find("[")
        string_content = string_content[start_idx:]

        end_idx = string_content.find("]")
        string_content = string_content[: (end_idx + 1)]

        to_remove_list: list = ast.literal_eval(string_content)
        return to_remove_list
