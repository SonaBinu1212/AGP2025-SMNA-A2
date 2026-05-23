"""
COSC2671 Social Media and Network Analytics
@author Sona Binu, S4137524, RMIT University, 2026

This script handles all the preprocessing before any analysis happens.
It loads the raw JSON, filters out videos not related to the Australian GP,
cleans the comment text, removes non-English comments, and samples down
to 15,000 if needed. The output is comments_clean.csv which feeds into
sentiment_analysis.py and topic_analysis.py.
"""

import json
import re
import pandas as pd
from langdetect import detect
import os

# ── Load data ─────────────────────────────────────────────
json_file = '../data/agp2025.json'
print(f"Loading from: {json_file}")

data = json.load(open(json_file, encoding='utf-8'))

# Flatten all comments across all videos into a single list,
# keeping track of which video each comment came from
all_comments = []
for video in data['videos']:
    for c in video['comments']:
        c['video_title'] = video['title']
    all_comments.extend(video['comments'])

df = pd.DataFrame(all_comments)
print(f"Total raw comments: {len(df)} from {df['video_title'].nunique()} videos")


# ── Filter: Keep only Australian GP related videos ────────
def is_agp_video(title):
    """
    Some search results sneak in unrelated videos, so this filters
    by checking if the video title actually mentions the Australian GP.
    """
    title_lower = title.lower()
    return any(kw in title_lower for kw in [
        'australian grand prix',
        'australia grand prix',
        'melbourne',
        'albert park',
        'australian gp',
        '2025 australian'
    ])

original_count = len(df)
df = df[df['video_title'].apply(is_agp_video)]
print(f"\nAfter AGP filter: {len(df)} comments (removed {original_count - len(df)} irrelevant)")
print("\nVideos kept:")
for v in df['video_title'].unique():
    print(f"  ✅ {v}")


# ── Clean text ────────────────────────────────────────────
def clean_text(text):
    """
    Basic text cleaning — removes URLs, mentions, special characters,
    and normalises whitespace. Converts to lowercase at the end.
    """
    text = str(text)
    text = re.sub(r"http\S+", "", text)         # remove URLs
    text = re.sub(r"@\w+", "", text)            # remove mentions
    text = re.sub(r"[^\w\s']", " ", text)       # remove special chars
    text = re.sub(r"\s+", " ", text).strip()    # normalise whitespace
    return text.lower()


# ── Filter English only ───────────────────────────────────
def is_english(text):
    """
    Uses langdetect to filter out non-English comments.
    Wrapped in try/except since very short or ambiguous text can throw errors.
    """
    try:
        return detect(str(text)) == "en"
    except:
        return False


print("\nCleaning text...")
df['clean_comment'] = df['text'].apply(clean_text)

# Drop very short comments and duplicates before running language detection
# (language detection is slow so worth trimming first)
df = df[df['clean_comment'].str.len() > 10]
df.drop_duplicates(subset='clean_comment', inplace=True)
print(f"After basic cleaning: {len(df)} comments")

print("Filtering English comments (this may take a few minutes)...")
df = df[df['clean_comment'].apply(is_english)]
print(f"After English filter: {len(df)} comments")


# ── If more than 15000, sample evenly across videos ───────
# Sampling proportionally so no single video dominates the dataset
if len(df) > 15000:
    df = df.groupby('video_title', group_keys=False).apply(
        lambda x: x.sample(min(len(x), int(15000 * len(x) / len(df)) + 1))
    ).head(15000)
    print(f"Sampled down to: {len(df)} comments (evenly across videos)")


# ── Dataset Summary ───────────────────────────────────────
print(f"\n=== Dataset Summary ===")
print(f"Total comments : {len(df)}")
print(f"Unique videos  : {df['video_title'].nunique()}")
print(f"Avg comment len: {df['clean_comment'].str.len().mean():.1f} chars")
print(f"Shortest       : {df['clean_comment'].str.len().min()} chars")
print(f"Longest        : {df['clean_comment'].str.len().max()} chars")
print(f"\nComments per video:")
print(df.groupby('video_title').size().sort_values(ascending=False))


# ── Save ──────────────────────────────────────────────────
df.to_csv('../data/comments_clean.csv', index=False, encoding='utf-8')
print("\nSaved to ../data/comments_clean.csv!")