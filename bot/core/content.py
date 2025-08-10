import trafilatura


class Content:
    """
    This is used to extract full article from the news-site.
    `Content` class here uses `trafilatura` for extracting main content from the requested web page.

    Parameters:
        url (str): link to the webpage.

    Returns:
        txt (str): news content.
    """

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
