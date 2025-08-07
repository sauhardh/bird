import requests

import logging
from config.constants import DISCORD_ACCEPT_WEBHOOK, DISCORD_REJECT_WEBHOOK


class DiscordWebhook:
    def __init__(self):
        self.flag = None

    def set_reject(self):
        self.flag = "reject"
        return self

    def set_accept(self):
        self.flag = "accept"
        return self

    def send(self, data: list[dict]):
        webhook_url = (
            DISCORD_ACCEPT_WEBHOOK if self.flag == "accept" else DISCORD_REJECT_WEBHOOK
        )

        color = 0xED4245 if self.flag == "reject" else 0x00FF00

        for obj in data:
            value = {
                "contents": "",
                "embeds": [
                    {
                        "title": obj["rephrased_title"],
                        "description": obj["rephrased_summary"],
                        "color": color,
                    }
                ],
            }

            response = requests.post(
                webhook_url,
                json=value,
            )

            if response.status_code == 204:
                logging.info(f"{self.flag}d news sent to discord channel successfully")
            else:
                logging.info(f"Failed to send {self.flag} to discord channel")

        return self
