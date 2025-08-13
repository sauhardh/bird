NUMBER_OF_NEWS: int = 5
VIRAL_TOKENS: set = {
    "trump",
    "shooting",
    "drugs",
    "gun",
    "illegal",
    "elon musk",
    "celebrity",
    "rapper",
    "war",
    "vulgar",
    "AI",
    "youtuber",
    "putin",
    "zelensky",
    "ukrane",
    "russia",
    "controversy",
    "Mr beast",
    "Modi",
    "prime minister",
    "president",
    "India",
    "disaster",
    "accident",
    "invention",
    "crash",
    "Trump",
    "elon",
}

AI_CONTENT_REPHRASE: str = f"""
You are an assistant to a social media content creator who shares breaking news stories with high viral potential.

Your goal:
- Select and rewrite only the **most viral** and **engaging** news articles.

What to include:
- Only include **real events** (not essays or opinions).
- Look for topics with **conflict, surprise, emotion, controversy, alerting**, or **famous figures**.
- Rephrase the title and summary to make them **short**, **punchy**, and **shocking** (without clickbaiting).

What to avoid:
- Do NOT choose generic, boring, or overly technical topics (e.g., "Plastic Credits", "UN Climate Agreements", "H1B Visa").
- Avoid essays, opinion, policy briefs, editorials, and content with no clear event or impact.
- Avoid vague activism topics or academic findings with no public reaction.
- Do NOT choose topics that are questions.

When writing the **rephrased title**:
- **Keep names of famous people** (like Trump, Elon Musk, Putin) when they appear in the original.
- Use emotionally engaging words like: “shocking”, “massive”, “slams”, “explodes”, “threatens”, “arrests”, “surges”.
- Create **urgency** and **curiosity** so users want to read more.

Also rate the story with a **viral_score (0 to 10)** based on current trends.

Current viral themes: {VIRAL_TOKENS}
"""

AI_CONTENT_FILTER = """
You are a precise and accurate duplicate detection assistant.

Rules:
- Always analyze news summaries for exact meaning duplicates.
- Use similarity scores from 1 (unrelated) to 10 (exact duplicate).
- Only consider pairs with similarity >= 9 as duplicates.
- News sharing topics but differing in facts, dates, or details are NOT duplicates.
- For duplicates groups, keep only the item with the smallest ID.
- Respond ONLY with a JSON list of duplicate IDs to remove.
- Do NOT provide explanations, comments, or any extra text.
- If no duplicates are found, respond with an empty list: [].
- Output must be a valid JSON array, e.g., [2,5,9].
"""

MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"

DISCORD_ACCEPT_WEBHOOK: str = "https://discord.com/api/webhooks/1402907173918605414/rR9D_G7IpjUMFtpJm1EJg_-rCdrzhQgRIL79adsxUNi-dYNAxSi6PXj7MpIXBvA_1QNq"
DISCORD_REJECT_WEBHOOK: str = " https://discord.com/api/webhooks/1402906383070007337/pcsCrYTUE2DMX-eAoXZ_ABUE995m2fTPOucgv7RWiFxt9fmzt0hImIDt-nBHqxCSTNMK"
DISCORD_INFO_WEBHOOK: str = "https://discord.com/api/webhooks/1403328283327856821/_iO4i3JyL2ydrawjHRDFsxsF4GXEcgBnsg5LBui0uThqv9eGCcGtH35vPTIv-7onjgTS"


CENSOR_WORDS: set = {
    # Violence-related terms
    "death",
    "die",
    "dead",
    "kill",
    "murder",
    "suicide",
    "rape",
    # Sexual content
    "sex",
    "porn",
    "fuck",
    "dick",
    "pussy",
    "ass",
    "tits",
    "erotic",
    # Profanity and slurs
    "bitch",
    "nigger",
    "nigga",
    "fag",
    "whore",
    "slut",
    "cunt",
    # Sensitive terms
    "nazi",
}


X_CHARACTER_LIMIT = 280
