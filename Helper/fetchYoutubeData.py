#
# COSC2671 Social Media and Network Analytics
# @author Sona Binu, S4137524, RMIT University, 2026
#
# This is the first script I wrote for the assignment — it handles
# all the data collection from YouTube. I used the YouTube Data API v3
# to search for videos about the 2025 Australian Grand Prix, then pulled
# the top-level comments from each video.
#
# The output is saved as a JSON file (agp2025.json) which gets used
# by all the other scripts in the pipeline (preprocessing, sentiment, etc.)
#
# You'll need a valid API key set up in youtubeClient.py before running this.
#
# Run with:
#   python fetchYoutubeData.py
#

import json
import sys
from youtubeClient import youtubeClient


def fetchYoutubeData(searchQuery, maxVideos=25, maxCommentsPerVideo=50, outputFile='youtubeDataDump.json'):
    """
    Searches YouTube for videos matching the query, fetches their comments,
    and dumps everything into a JSON file for offline analysis.

    @param searchQuery: what to search for (e.g. 'Australian Grand Prix 2025')
    @param maxVideos: how many videos to pull (I used 50 for the assignment)
    @param maxCommentsPerVideo: comment limit per video
    @param outputFile: where to save the output
    """

    client = youtubeClient()

    # Search for videos matching the query, sorted by view count
    # so we get the most popular/relevant ones first
    print(f"Searching for videos with query: '{searchQuery}'...")
    searchResponse = client.search().list(
        q=searchQuery,
        part='snippet',
        type='video',
        order='viewCount',
        maxResults=min(maxVideos, 50)  # API hard limit is 50 per request
    ).execute()

    videoIds = []
    videoSnippets = {}
    for item in searchResponse.get('items', []):
        videoId = item['id']['videoId']
        videoIds.append(videoId)
        videoSnippets[videoId] = item['snippet']

    print(f"  Found {len(videoIds)} videos.")

    # Pull view and like counts for each video — useful for context
    # even if I didn't end up using these in the final analysis
    print("Fetching video statistics...")
    statsResponse = client.videos().list(
        id=','.join(videoIds),
        part='statistics'
    ).execute()

    videoStats = {}
    for item in statsResponse.get('items', []):
        videoStats[item['id']] = item['statistics']

    # Now go through each video and grab its comments
    # Some videos have comments disabled which throws an exception,
    # so I wrapped it in a try/except to keep the loop going
    print("Fetching comments...")
    videos = []

    for videoId in videoIds:
        snippet = videoSnippets[videoId]
        stats = videoStats.get(videoId, {})

        video = {
            'title': snippet['title'],
            'videoId': videoId,
            'channelTitle': snippet['channelTitle'],
            'publishedAt': snippet['publishedAt'],
            'viewCount': int(stats.get('viewCount', 0)),
            'likeCount': int(stats.get('likeCount', 0)),
            'comments': []
        }

        try:
            commentResponse = client.commentThreads().list(
                videoId=videoId,
                part='snippet',
                maxResults=maxCommentsPerVideo,
                textFormat='plainText'
            ).execute()

            for commentThread in commentResponse.get('items', []):
                topComment = commentThread['snippet']['topLevelComment']['snippet']
                video['comments'].append({
                    'author': topComment['authorDisplayName'],
                    'text': topComment['textDisplay'],
                    'publishedAt': topComment['publishedAt'],
                    'likeCount': topComment.get('likeCount', 0)
                })

            print(f"  {snippet['title'][:50]}... → {len(video['comments'])} comments")

        except Exception as e:
            print(f"  {snippet['title'][:50]}... → Comments disabled or error: {e}")

        videos.append(video)

    # Save everything to JSON — this becomes the raw data file
    # that all the other scripts read from
    data = {'videos': videos}
    with open(outputFile, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Saved {len(videos)} videos to '{outputFile}'.")


# ============================================================
# Main — parameters I used for the AGP 2025 dataset
# ============================================================

if __name__ == '__main__':
    SEARCH_QUERY = 'Australian Grand Prix 2025'
    MAX_VIDEOS = 50
    MAX_COMMENTS = None
    OUTPUT_FILE = '../data/agp2025.json'

    fetchYoutubeData(SEARCH_QUERY, MAX_VIDEOS, MAX_COMMENTS, OUTPUT_FILE)