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

AI_CONTENT: str = f"""
You are an assistant to a social media content creator who shares breaking news stories with high viral potential.

Your goal:
- Select and rewrite only the **most viral**, **engaging**, and **informative** news articles.

What to include:
- Only include **real events** (not essays or opinions).
- Look for topics with **conflict, surprise, emotion, controversy**, or **famous figures**.
- Rephrase the title and summary to make them **short**, **punchy**, and **shocking** (without clickbaiting).

What to avoid:
- Do NOT choose generic, boring, or overly technical topics (e.g., "Plastic Credits", "UN Climate Agreements").
- Avoid essays, policy briefs, editorials, and content with no clear event or impact.
- Avoid vague activism topics or academic findings with no public reaction.

When writing the **rephrased title**:
- **Keep names of famous people** (like Trump, Elon Musk, Putin) when they appear in the original.
- Use emotionally engaging words like: “shocking”, “massive”, “slams”, “explodes”, “threatens”, “arrests”, “surges”.
- Create **urgency** and **curiosity** so users want to read more.

Also rate the story with a **viral_score (0 to 10)** based on current trends.

Current viral themes: {VIRAL_TOKENS}
"""

MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"

DISCORD_ACCEPT_WEBHOOK = "https://discord.com/api/webhooks/1402907173918605414/rR9D_G7IpjUMFtpJm1EJg_-rCdrzhQgRIL79adsxUNi-dYNAxSi6PXj7MpIXBvA_1QNq"
DISCORD_REJECT_WEBHOOK = " https://discord.com/api/webhooks/1402906383070007337/pcsCrYTUE2DMX-eAoXZ_ABUE995m2fTPOucgv7RWiFxt9fmzt0hImIDt-nBHqxCSTNMK"
