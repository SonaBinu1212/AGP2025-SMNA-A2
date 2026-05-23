#
# COSC2671 Social Media and Network Analytics
# @author Sona Binu, S4137524, RMIT University, 2026
#
# This is an updated version of fetchYoutubeData.py — the main difference
# is that this one supports pagination, so it can fetch ALL comments from
# a video rather than being capped at 50. I needed this to build a larger
# dataset for the analysis.
#
# Run with:
#   python fetchYoutubeData_20260330.py
#
# Make sure your API key is set in youtubeClient.py first.
#

import json
import sys
from youtubeClient import youtubeClient


def fetchYoutubeData(searchQuery, maxVideos=25, maxCommentsPerVideo=None, outputFile='youtubeDataDump.json'):
    """
    Searches YouTube for videos and fetches their comments, with pagination
    support to get beyond the 100-comment API limit per request.

    @param searchQuery: search term (e.g. 'Australian Grand Prix 2025')
    @param maxVideos: number of videos to retrieve
    @param maxCommentsPerVideo: cap on comments per video — set to None to fetch all
    @param outputFile: where to write the JSON output
    """

    client = youtubeClient()

    print(f"Searching for videos with query: '{searchQuery}'...")
    searchResponse = client.search().list(
        q=searchQuery,
        part='snippet',
        type='video',
        order='viewCount',
        maxResults=min(maxVideos, 50)  # API hard limit per request is 50
    ).execute()

    videoIds = []
    videoSnippets = {}
    for item in searchResponse.get('items', []):
        videoId = item['id']['videoId']
        videoIds.append(videoId)
        videoSnippets[videoId] = item['snippet']

    print(f"  Found {len(videoIds)} videos.")

    print("Fetching video statistics...")
    statsResponse = client.videos().list(
        id=','.join(videoIds),
        part='statistics'
    ).execute()

    videoStats = {}
    for item in statsResponse.get('items', []):
        videoStats[item['id']] = item['statistics']

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
            comments_fetched = 0
            next_page_token = None

            # Keep looping through pages until we hit the limit or run out of comments
            while True:
                if maxCommentsPerVideo is not None:
                    request_limit = min(100, maxCommentsPerVideo - comments_fetched)
                else:
                    request_limit = 100  # max the API allows per request

                commentResponse = client.commentThreads().list(
                    videoId=videoId,
                    part='snippet',
                    maxResults=request_limit,
                    pageToken=next_page_token,
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
                    comments_fetched += 1

                    if maxCommentsPerVideo is not None and comments_fetched >= maxCommentsPerVideo:
                        break

                if maxCommentsPerVideo is not None and comments_fetched >= maxCommentsPerVideo:
                    break

                # Move to next page (if there isn't one, we're done)
                next_page_token = commentResponse.get('nextPageToken')
                if not next_page_token:
                    break

            print(f"  {snippet['title'][:50]}... → {len(video['comments'])} comments")

        except Exception as e:
            # Some videos have comments turned off — just skip and continue
            print(f"  {snippet['title'][:50]}... → Comments disabled or error: {e}")

        videos.append(video)

    # Write everything out to JSON for use in the rest of the pipeline
    data = {'videos': videos}
    with open(outputFile, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Saved {len(videos)} videos to '{outputFile}'.")


# ============================================================
# Main — parameters used to collect the AGP 2025 dataset
# ============================================================

if __name__ == '__main__':
    SEARCH_QUERY = 'Australian Grand Prix 2025'
    MAX_VIDEOS = 50
    MAX_COMMENTS = None  # fetch all available comments
    OUTPUT_FILE = '../data/agp2025.json'

    fetchYoutubeData(SEARCH_QUERY, MAX_VIDEOS, MAX_COMMENTS, OUTPUT_FILE)