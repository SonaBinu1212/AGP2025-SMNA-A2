"""
COSC2671 Social Media and Network Analytics
@author Sona Binu, S4137524, RMIT University, 2026

I wrote this script to expand the dataset beyond what a single search query
could return. By running multiple targeted queries about the 2025 Australian GP,
I was able to pull more videos and get a larger, more diverse comment set.

It also filters out any videos that aren't actually about the Australian GP
(since search results can sometimes be noisy), and deduplicates videos that
show up across multiple queries.

Output: ../data/agp2025_merged.json — the combined dataset used for analysis.
"""

from fetchYoutubeData_20260330 import fetchYoutubeData
import json, os

# Different search angles for the same event — helps surface more videos
queries = [
    'Australian Grand Prix 2025',
    '2025 Australian GP race',
    'Melbourne F1 2025',
    'Albert Park Grand Prix 2025',
]

all_videos = []

for query in queries:
    print(f"\nFetching: {query}")
    fname = f'../data/temp_{query[:15].replace(" ","_")}.json'
    fetchYoutubeData(
        searchQuery=query,
        maxVideos=25,
        maxCommentsPerVideo=None,
        outputFile=fname
    )

    if os.path.exists(fname):
        data = json.load(open(fname, encoding='utf-8'))

        # Only keep videos that are actually about the Australian GP —
        # some results from broader queries are unrelated
        for v in data['videos']:
            title_lower = v['title'].lower()
            if any(kw in title_lower for kw in ['australia', 'melbourne', 'albert park', 'agp']):
                all_videos.append(v)
                print(f"  KEPT: {v['title'][:60]}")
            else:
                print(f"  SKIPPED: {v['title'][:60]}")

# The same video can appear in multiple query results, so deduplicate by videoId
seen = set()
unique_videos = []
for v in all_videos:
    if v['videoId'] not in seen:
        seen.add(v['videoId'])
        unique_videos.append(v)

print(f"\nTotal unique AGP videos: {len(unique_videos)}")
total_comments = sum(len(v['comments']) for v in unique_videos)
print(f"Total comments: {total_comments}")

# Save the merged dataset — this is what gets used in preprocess.py onwards
with open('../data/agp2025_merged.json', 'w', encoding='utf-8') as f:
    json.dump({'videos': unique_videos}, f, ensure_ascii=False, indent=2)
print("Saved to ../data/agp2025_merged.json!")