"""
COSC2671 Social Media and Network Analytics
@author Sona Binu, S4137524, RMIT University, 2026

Sets up the YouTube Data API v3 client used by all the data fetching scripts.
Adapted from the lab's Reddit/PRAW client setup.
"""

import sys
from googleapiclient.discovery import build


def youtubeClient():
    """
    Builds and returns an authenticated YouTube API service object.
    Replace the apiKey value with your own before running.

    @returns: YouTube API service object
    """

    try:
        # Replace with your own API key
        apiKey = "YOUR_API_KEY_HERE"

        youtube = build('youtube', 'v3', developerKey=apiKey)

    except Exception as e:
        sys.stderr.write("Failed to create YouTube client: {}\n".format(str(e)))
        sys.exit(1)

    return youtube