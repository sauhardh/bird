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
You are an expert news analyst assistant.

You will be given a list of news items in the format:
[ {id1: "news_summary1"}, {id2: "news_summary2"}, ... ]

Your role:
- Carefully analyze every news summary for meaning and context.
- Determine which news items convey the exact same news story.
- Use a similarity scale from 1 (completely different) to 10 (exact duplicates).
- Mark items as duplicates only if similarity score is 9 or above.
- For each group of duplicates, keep the one with the smallest ID.
- Return only a JSON list of duplicate IDs to remove.
- Do not provide any explanations or additional text.
- Avoid false positives; be conservative and precise.

Example:
Input:
[
  {1: "Biden meets Zelensky to discuss Ukraine aid"},
  {2: "US President Biden holds talks with Ukraine's Zelensky on military support"},
  {3: "Massive earthquake hits Japan, thousands affected"},
  {4: "Japan struck by powerful earthquake causing widespread damage"}
]

Output:
[1, 3]
"""

MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"

DISCORD_ACCEPT_WEBHOOK: str = "https://discord.com/api/webhooks/1402907173918605414/rR9D_G7IpjUMFtpJm1EJg_-rCdrzhQgRIL79adsxUNi-dYNAxSi6PXj7MpIXBvA_1QNq"
DISCORD_REJECT_WEBHOOK: str = " https://discord.com/api/webhooks/1402906383070007337/pcsCrYTUE2DMX-eAoXZ_ABUE995m2fTPOucgv7RWiFxt9fmzt0hImIDt-nBHqxCSTNMK"
DISCORD_INFO_WEBHOOK: str = "https://discord.com/api/webhooks/1403328283327856821/_iO4i3JyL2ydrawjHRDFsxsF4GXEcgBnsg5LBui0uThqv9eGCcGtH35vPTIv-7onjgTS"
