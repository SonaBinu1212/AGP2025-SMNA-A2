"""
COSC2671 Social Media and Network Analytics
@author Sona Binu, S4137524, RMIT University, 2026

A reusable text processing class for YouTube comments and video titles.
I adapted this from the RedditProcessing.py provided in the labs — the core
NLP logic is platform-agnostic so it works just as well for YouTube text.
It gets imported by the preprocessing and analysis scripts in the pipeline.
"""

import re


class YouTubeProcessing:
    """
    Centralises text preprocessing in one place so I don't repeat the same
    tokenisation and filtering logic across multiple scripts.
    """

    def __init__(self, tokeniser, lStopwords):
        """
        @param tokeniser: NLTK tokeniser (e.g. TweetTokenizer)
        @param lStopwords: list of stopwords to remove
        """
        self.tokeniser = tokeniser
        self.lStopwords = lStopwords

    def process(self, text):
        """
        Tokenises and filters a piece of text, removing stopwords,
        URLs, and numeric tokens.

        @param text: the comment or video title to process
        @returns: list of clean tokens
        """
        text = text.lower()
        tokens = self.tokeniser.tokenize(text)
        tokensStripped = [tok.strip() for tok in tokens]

        # Regex to catch standalone digits and fractions (e.g. 6.15)
        regexDigit = re.compile(r"^\d+\s|\s\d+\s|\s\d+$")
        regexHttp = re.compile(r"^http")

        return [tok for tok in tokensStripped
                if tok not in self.lStopwords
                and regexDigit.match(tok) is None
                and regexHttp.match(tok) is None]