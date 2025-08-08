import requests

import logging
from config.constants import (
    DISCORD_ACCEPT_WEBHOOK,
    DISCORD_REJECT_WEBHOOK,
    DISCORD_INFO_WEBHOOK,
)


class DiscordWebhook:
    def __init__(self):
        self.flag = None

    def set_reject(self):
        self.flag = "reject"
        return self

    def set_accept(self):
        self.flag = "accept"
        return self

    def set_info(self):
        self.flag = "info"
        return self

    def send_info(self, title: str, info: str):
        if self.flag == "info":
            data = {
                "contents": "",
                "embeds": {"title": title, "description": info, "color": 3447003},
            }

            response = requests.post(DISCORD_INFO_WEBHOOK, json=data)
            if response.status_code == 204:
                logging.info(f"{self.flag}d sent to discord channel successfully")
            else:
                logging.info(f"Failed to send {self.flag} to discord channel")

        return self

    def send(self, data: list[dict]):
        webhook_url: str

        match self.flag:
            case "accept":
                webhook_url = DISCORD_ACCEPT_WEBHOOK
            case "reject":
                webhook_url = DISCORD_REJECT_WEBHOOK

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
