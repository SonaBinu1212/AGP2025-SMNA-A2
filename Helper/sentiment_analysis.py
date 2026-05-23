"""
COSC2671 Social Media and Network Analytics
@author Sona Binu, S4137524, RMIT University, 2026

This script runs sentiment analysis on the cleaned comments using VADER.
I chose VADER over other approaches because it's specifically built for
social media text — it handles things like capitalisation, slang, and
punctuation (e.g. "AMAZING!!!") without needing any training data.

It reads from comments_clean.csv and outputs:
  - Four visualisations (bar chart, pie chart, over time, by video)
  - comments_with_sentiment.csv with sentiment labels and compound scores
"""

import pandas as pd
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon')

# ── Load cleaned data ──────────────────────────────────────
df = pd.read_csv('../data/comments_clean.csv', encoding='utf-8')
print(f"Loaded {len(df)} comments")
print("Columns available:", df.columns.tolist())


# ── VADER Sentiment Analysis ───────────────────────────────
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    """
    Returns a sentiment label and compound score for a given comment.
    Thresholds follow VADER's recommended values (>= 0.05 positive, <= -0.05 negative).
    """
    scores = analyzer.polarity_scores(str(text))
    compound = scores['compound']
    if compound >= 0.05:
        return 'positive', compound
    elif compound <= -0.05:
        return 'negative', compound
    else:
        return 'neutral', compound

print("Running sentiment analysis...")
df[['sentiment', 'compound_score']] = df['clean_comment'].apply(
    lambda x: pd.Series(get_sentiment(x))
)

# ── Basic Stats ────────────────────────────────────────────
print("\n=== Sentiment Distribution ===")
print(df['sentiment'].value_counts())
print(f"\nAverage compound score: {df['compound_score'].mean():.4f}")

# Handle both possible column names from preprocessing
text_col = 'text' if 'text' in df.columns else 'clean_comment'
print(f"\nMost positive comment:\n  {df.loc[df['compound_score'].idxmax(), text_col]}")
print(f"\nMost negative comment:\n  {df.loc[df['compound_score'].idxmin(), text_col]}")


# ── Plot 1: Bar chart ──────────────────────────────────────
counts = df['sentiment'].value_counts()
colors = ['#2ecc71', '#e74c3c', '#95a5a6']
plt.figure(figsize=(8, 5))
counts.plot(kind='bar', color=colors)
plt.title('Sentiment Distribution — Australian Grand Prix 2025')
plt.xlabel('Sentiment')
plt.ylabel('Number of Comments')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('plot_sentiment_distribution.png', dpi=150)
plt.show()
print("Saved: plot_sentiment_distribution.png")


# ── Plot 2: Pie chart ──────────────────────────────────────
plt.figure(figsize=(6, 6))
counts.plot(kind='pie',
            colors=['#2ecc71', '#e74c3c', '#95a5a6'],
            autopct='%1.1f%%',
            startangle=90)
plt.title('Sentiment Breakdown — AGP 2025')
plt.ylabel('')
plt.tight_layout()
plt.savefig('plot_sentiment_pie.png', dpi=150)
plt.show()
print("Saved: plot_sentiment_pie.png")


# ── Plot 3: Sentiment over time ────────────────────────────
# Resampled weekly to smooth out day-to-day noise
date_col = 'published_at' if 'published_at' in df.columns else 'publishedAt'
print(f"\nUsing date column: {date_col}")

df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
df_time = df.dropna(subset=[date_col]).copy()
df_time = df_time.set_index(date_col)
weekly = df_time['compound_score'].resample('W').mean()

plt.figure(figsize=(12, 4))
plt.plot(weekly.index, weekly.values, marker='o', color='#3498db')
plt.axhline(y=0, color='red', linestyle='--', alpha=0.5)
plt.title('Average Sentiment Over Time — AGP 2025')
plt.xlabel('Week')
plt.ylabel('Average Compound Score')
plt.tight_layout()
plt.savefig('plot_sentiment_over_time.png', dpi=150)
plt.show()
print("Saved: plot_sentiment_over_time.png")


# ── Plot 4: Sentiment by video ─────────────────────────────
# Useful for seeing whether certain videos attracted more negative responses
video_col = 'video_title' if 'video_title' in df.columns else 'videoId'
print(f"Using video column: {video_col}")

plt.figure(figsize=(12, 6))
video_sentiment = df.groupby(video_col)['compound_score'].mean().sort_values()
video_sentiment.index = [t[:40] + '...' if len(t) > 40 else t
                          for t in video_sentiment.index]
colors_bar = ['#e74c3c' if x < 0 else '#2ecc71' for x in video_sentiment.values]
video_sentiment.plot(kind='barh', color=colors_bar)
plt.title('Average Sentiment by Video — AGP 2025')
plt.xlabel('Average Compound Score')
plt.axvline(x=0, color='black', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('plot_sentiment_by_video.png', dpi=150)
plt.show()
print("Saved: plot_sentiment_by_video.png")


# ── Save results ───────────────────────────────────────────
df.to_csv('../data/comments_with_sentiment.csv', index=False, encoding='utf-8')
print("\nSaved: ../data/comments_with_sentiment.csv")


# ── Final Summary ──────────────────────────────────────────
print("\n=== Final Summary ===")
print(f"Total comments analysed : {len(df)}")
print(f"Positive : {(df['sentiment']=='positive').sum()} ({(df['sentiment']=='positive').mean()*100:.1f}%)")
print(f"Neutral  : {(df['sentiment']=='neutral').sum()} ({(df['sentiment']=='neutral').mean()*100:.1f}%)")
print(f"Negative : {(df['sentiment']=='negative').sum()} ({(df['sentiment']=='negative').mean()*100:.1f}%)")
print(f"Average compound score  : {df['compound_score'].mean():.4f}")
print("\n=== Done! All charts saved. ===")