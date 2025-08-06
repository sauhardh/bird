import trafilatura


class Content:
    link: str

    def __init__(self, url: str):
        self.link = url

    def get_content(self) -> str:
        downloaded = trafilatura.fetch_url(self.link)
        output = trafilatura.extract(
            downloaded,
            include_comments=False,
            favor_precision=True,
        )

        return output
