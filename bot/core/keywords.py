import spacy
from spacy import Language

import logging
import subprocess


class Keyword:
    nlp: Language

    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logging.info("Installing `en_core_web_sm` module from spacy")
            subprocess.run(
                ["python", "-m", "spacy", "download", "en_core_web_sm"],
                check=True,
                capture_output=True,
                text=True,
            )
            logging.info("Installation complete!. Loading `en_core_web_sm`")
            self.nlp = spacy.load("en_core_web_sm")

    def extract_entities(self, text: str) -> str | None:
        doc = self.nlp(text)
        entities = [
            ent.text for ent in doc.ents if ent.label_ in ("PERSON", "GPE", "ORG")
        ]

        if len(entities) <= 0:
            return None

        return " ".join(entities[:2])
