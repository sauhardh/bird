from groq import Groq
import time
import logging
import json
import ast

from config.constants import MODEL, AI_CONTENT_REPHRASE, AI_CONTENT_FILTER
from .content import Content


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
                Should feel natural, like a real user posting about it.

            3. Score the **viral potential** from 0 to 10 based on:
            - Public interest
            - Relevance to trending topics
            - Involvement of celebrities, politics, scandals, or surprising developments

            📌 Only reply with a JSON object in **this exact format**:

            {{
            "viral_score": 0-10 (10 being highest),
            "viral": true/false,
            "title": "...",  // original
            "rephrased_title": "...", 
            "rephrased_summary": "..."
            }}

            Critical: Do not add extra any information or explanation, **no nothing extra**.
            """

            messages = [
                {"role": "assistant", "content": AI_CONTENT_REPHRASE},
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

            string_content["link"] = article.get("link", None)
            string_content["published"] = article.get("published", None)
            string_content["thumbnail"] = article.get("thumbnail", None)

            rephrased_news_list.append(string_content)

        return rephrased_news_list

    def find_duplicate(self, news_list: dict) -> list:
        formatted_news_list: list[dict] = [
            {news["id"]: news["rephrased_summary"]} for news in news_list
        ]

        formatted_news_json = json.dumps(
            formatted_news_list, ensure_ascii=False, indent=2
        )

        user_content: str = f"""
        You are given a list of news items in this format:

        {formatted_news_json}

        Your task:
        - Compare each news summary with every other summary.
        - Assign a similarity score from 1 (unrelated) to 10 (exact duplicate).
        - If two news has same meaning but different words, it is considered duplicate else not duplicate.
        - Mark as duplicates ONLY those pairs with similarity score >= 9.
        - News about the same topic but with different facts, dates are NOT duplicates.
        - From each group of duplicates, keep the news item with the smallest ID.
        - Return ONLY a JSON list of IDs of duplicate news items to be removed.
        - DO NOT output any explanations or extra text, ONLY the JSON list.

        Example:
        Input:
        [
        {{1: "Biden meets Zelensky about military aid"}},
        {{2: "US President Biden holds talks with Zelensky on aid"}},
        {{3: "Earthquake hits Japan, many injured"}}
        ]

        Similarity scores:
        - News 1 & 2: 9 (duplicate, so select id 1)
        - News 3: 1 (not duplicate)

        Output:
        [1]


        📌 Critical: Only reply with a JSON list in **this exact format** (Do not add single extra information, not at all):
        [id, id]
        """

        messages = [
            {"role": "assistant", "content": AI_CONTENT_FILTER},
            {"role": "user", "content": user_content},
        ]

        chat_completion = self.client.chat.completions.create(
            messages=messages, model=self.model
        )

        string_content: str = chat_completion.choices[0].message.content
        print("string_content", string_content)

        to_remove_list: list = ast.literal_eval(string_content)

        return to_remove_list
