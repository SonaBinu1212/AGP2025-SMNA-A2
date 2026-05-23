"""
COSC2671 Social Media and Network Analytics
@author Sona Binu, S4137524, RMIT University, 2026

This script generates the word cloud visualisations used in the report.
It produces two figures — an overall word cloud across all comments,
and a side-by-side comparison of positive vs negative comment vocabulary.

Reads from: ../data/comments_clean.csv, ../data/comments_with_sentiment.csv
Outputs:
  - wordcloud_all.png
  - wordcloud_by_sentiment.png
"""

import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')

df = pd.read_csv('../data/comments_clean.csv', encoding='utf-8')

stop_words = set(stopwords.words('english'))

# Added F1-specific terms that are too generic to be meaningful in a word cloud
# (they'd dominate every cloud regardless of sentiment or topic)
stop_words.update(['f1', 'race', 'grand', 'prix', 'formula', 'one',
                   'car', 'lap', 'driver', 'would', 'like', 'just',
                   'got', 'get', 'still', 'even', 'know', 'think'])


# ── Overall word cloud ─────────────────────────────────────
all_text = ' '.join(df['clean_comment'].astype(str))

wordcloud = WordCloud(
    width=1200,
    height=600,
    background_color='white',
    stopwords=stop_words,
    max_words=100,
    colormap='RdYlGn'
).generate(all_text)

plt.figure(figsize=(14, 7))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Most Common Words — AGP 2025 YouTube Comments', fontsize=16)
plt.tight_layout()
plt.savefig('wordcloud_all.png', dpi=150)
plt.show()
print("Saved: wordcloud_all.png")


# ── Sentiment word clouds ──────────────────────────────────
# Load the sentiment-labelled dataset and split by positive/negative
df_sa = pd.read_csv('../data/comments_with_sentiment.csv', encoding='utf-8')

pos_text = ' '.join(df_sa[df_sa['sentiment'] == 'positive']['clean_comment'].astype(str))
neg_text = ' '.join(df_sa[df_sa['sentiment'] == 'negative']['clean_comment'].astype(str))

wordcloud_pos = WordCloud(
    width=800, height=400,
    background_color='white',
    stopwords=stop_words,
    max_words=80,
    colormap='Greens'
).generate(pos_text)

wordcloud_neg = WordCloud(
    width=800, height=400,
    background_color='white',
    stopwords=stop_words,
    max_words=80,
    colormap='Reds'
).generate(neg_text)

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

axes[0].imshow(wordcloud_pos, interpolation='bilinear')
axes[0].axis('off')
axes[0].set_title('Positive Comments', fontsize=14, color='green')

axes[1].imshow(wordcloud_neg, interpolation='bilinear')
axes[1].axis('off')
axes[1].set_title('Negative Comments', fontsize=14, color='red')

plt.suptitle('Word Clouds by Sentiment — AGP 2025', fontsize=16)
plt.tight_layout()
plt.savefig('wordcloud_by_sentiment.png', dpi=150)
plt.show()
print("Saved: wordcloud_by_sentiment.png")