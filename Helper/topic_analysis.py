"""
COSC2671 Social Media and Network Analytics
@author Sona Binu, S4137524, RMIT University, 2026

This script runs LDA topic modelling on the cleaned comments to identify
the main themes in fan discussion around the 2025 Australian GP.

I used Gensim's LDA implementation with 5 topics after some experimentation —
fewer topics were too broad and more started to overlap. The text goes through
tokenisation, stemming, and stopword removal before being fed into the model.

Reads from: ../data/comments_clean.csv
Outputs:
  - plot_lda_topics.png
  - plot_topic_distribution.png
  - ../data/comments_with_topics.csv
"""

import pandas as pd
import matplotlib.pyplot as plt
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk
import string
from gensim import corpora
from gensim.models import LdaModel
import warnings
warnings.filterwarnings('ignore')

nltk.download('stopwords')


def process_for_lda(text, tokenizer, stemmer, stop_words, punctuation):
    """
    Tokenises, stems, and filters a comment for LDA input.
    Removes stopwords, punctuation, digits, and very short tokens.
    """
    text = str(text).lower()
    tokens = tokenizer.tokenize(text)
    tokens = [stemmer.stem(t) for t in tokens
              if t not in stop_words
              and t not in punctuation
              and not t.isdigit()
              and len(t) > 2]
    return tokens


if __name__ == '__main__':

    # ── Load data ──────────────────────────────────────────
    df = pd.read_csv('../data/comments_clean.csv', encoding='utf-8')
    print(f"Loaded {len(df)} comments")

    # ── Setup NLP tools ────────────────────────────────────
    tokenizer = TweetTokenizer()
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words('english'))
    punctuation = set(string.punctuation)

    # Added domain-specific stopwords that are too common to be meaningful
    # for topic modelling (e.g. 'f1', 'race', 'watch' appear in almost every comment)
    stop_words.update([
        'f1', 'race', 'grand', 'prix', 'formula', 'one', 'car', 'lap',
        'driver', 'would', 'like', 'just', 'got', 'get', 'still', 'even',
        'know', 'think', 'really', 'watch', 'watching', 'year', 'time',
        'good', 'great', 'make', 'going', 'come', 'back', 'also', 'way',
        'first', 'last', 'well', 'much', 'said', 'see', 'want', 'need',
        'australian', 'australia', 'gp', '2025', 'highlight', 'highlights'
    ])

    # ── Process tokens ─────────────────────────────────────
    print("Processing text for LDA...")
    df['tokens'] = df['clean_comment'].apply(
        lambda x: process_for_lda(x, tokenizer, stemmer, stop_words, punctuation)
    )
    df = df[df['tokens'].map(len) > 0]
    print(f"Comments with valid tokens: {len(df)}")

    # ── Build dictionary and corpus ────────────────────────
    print("Building dictionary and corpus...")
    dictionary = corpora.Dictionary(df['tokens'])

    # Filter out very rare and very common terms — they don't help distinguish topics
    dictionary.filter_extremes(no_below=10, no_above=0.4)
    print(f"Dictionary size: {len(dictionary)} unique tokens")
    corpus = [dictionary.doc2bow(tokens) for tokens in df['tokens']]

    # ── Train LDA ──────────────────────────────────────────
    NUM_TOPICS = 5
    print(f"\nTraining LDA model with {NUM_TOPICS} topics...")
    lda_model = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=NUM_TOPICS,
        random_state=42,
        passes=15,
        alpha='auto'
    )

    # ── Print topics ───────────────────────────────────────
    print("\n=== Discovered Topics ===")
    for idx, topic in lda_model.print_topics(num_words=10):
        words = [w.split('*')[1].replace('"', '').strip()
                 for w in topic.split('+')]
        print(f"\nTopic {idx + 1}: {', '.join(words)}")

    # ── Plot topics ────────────────────────────────────────
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
    fig, axes = plt.subplots(1, NUM_TOPICS, figsize=(18, 6))

    for idx in range(NUM_TOPICS):
        topic_words = dict(lda_model.show_topic(idx, topn=10))
        words = list(topic_words.keys())
        scores = list(topic_words.values())
        axes[idx].barh(words, scores, color=colors[idx])
        axes[idx].set_title(f'Topic {idx + 1}', fontsize=12, fontweight='bold')
        axes[idx].set_xlabel('Word Probability')
        axes[idx].invert_yaxis()

    plt.suptitle('LDA Topic Analysis — AGP 2025 YouTube Comments',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('plot_lda_topics.png', dpi=150)
    plt.show()
    print("Saved: plot_lda_topics.png")

    # ── Topic distribution ─────────────────────────────────
    # Assign each comment to its dominant topic for the distribution chart
    topic_assignments = []
    for bow in corpus:
        topics = lda_model.get_document_topics(bow)
        if topics:
            dominant = max(topics, key=lambda x: x[1])
            topic_assignments.append(dominant[0])
        else:
            topic_assignments.append(0)

    df['dominant_topic'] = topic_assignments[:len(df)]
    topic_counts = df['dominant_topic'].value_counts().sort_index()

    plt.figure(figsize=(10, 5))
    bars = plt.bar(
        [f'Topic {i+1}' for i in topic_counts.index],
        topic_counts.values,
        color=colors[:len(topic_counts)]
    )
    plt.title('Comment Distribution Across Topics — AGP 2025')
    plt.xlabel('Topic')
    plt.ylabel('Number of Comments')
    for bar, count in zip(bars, topic_counts.values):
        plt.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 50,
                 str(count), ha='center', fontsize=10)
    plt.tight_layout()
    plt.savefig('plot_topic_distribution.png', dpi=150)
    plt.show()
    print("Saved: plot_topic_distribution.png")

    # ── Save results ───────────────────────────────────────
    df.to_csv('../data/comments_with_topics.csv', index=False, encoding='utf-8')
    print("\nSaved: ../data/comments_with_topics.csv")
    print("\n=== Topic Analysis Complete! ===")