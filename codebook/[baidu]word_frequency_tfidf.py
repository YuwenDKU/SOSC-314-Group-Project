# ============================================================
# WORD FREQUENCY + TF-IDF ANALYSIS
# ============================================================

import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import jieba

INPUT_XLSX = Path("tieba_clean/tieba_posts.xlsx")
OUTPUT_XLSX = Path("tieba_clean/word_frequency_tfidf.xlsx")

# ---------- load cleaned posts ----------

df = pd.read_excel(INPUT_XLSX, sheet_name="posts")

texts = df["tokens_joined"].astype(str).tolist()

print(f"Analyzing {len(texts)} posts...\n")

# ---------- chinese tokenizer ----------

def chinese_tokenizer(text):
    return [
        w.strip()
        for w in jieba.lcut(str(text))
        if w.strip()
    ]

# ---------- word frequency ----------

count_vectorizer = CountVectorizer(
    tokenizer=chinese_tokenizer,
    token_pattern=None,
    max_df=0.8,
    min_df=2
)

count_dtm = count_vectorizer.fit_transform(texts)
words = count_vectorizer.get_feature_names_out()

word_count = count_dtm.sum(axis=0).A1
document_frequency = (count_dtm > 0).sum(axis=0).A1

# ---------- TF-IDF ----------
tfidf_vectorizer = TfidfVectorizer(
    tokenizer=chinese_tokenizer,
    token_pattern=None,
    max_df=0.8,
    min_df=2
)

tfidf_dtm = tfidf_vectorizer.fit_transform(texts)
mean_tfidf = tfidf_dtm.mean(axis=0).A1

# ---------- Combine ----------
results_df = pd.DataFrame({
    "word": words,
    "count": word_count,
    "document_frequency": document_frequency,
    "tf_idf": mean_tfidf
})

# ---------- Top 50 by frequency ----------
top_50 = results_df.sort_values(
    "count", ascending=False
).head(50).reset_index(drop=True)

top_50.insert(0, "rank", range(1, 51))

print("TOP 50 WORDS")
print(top_50.to_string(index=False))

# ---------- Top 50 by TF-IDF ----------
top_50_tfidf = results_df.sort_values(
    "tf_idf", ascending=False
).head(50).reset_index(drop=True)

top_50_tfidf.insert(0, "rank", range(1, 51))

print("\nTOP 50 WORDS BY MEAN TF-IDF")
print(top_50_tfidf.to_string(index=False))


# ============================================================
# SAVE TO EXCEL
# ============================================================

with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:

    # Main combined table
    top_50[
        ["rank", "word", "count", "document_frequency", "tf_idf"]
    ].to_excel(
        writer,
        sheet_name="top_50_words",
        index=False
    )

    # Top TF-IDF
    top_50_tfidf[
        ["rank", "word", "count", "document_frequency", "tf_idf"]
    ].to_excel(
        writer,
        sheet_name="top_50_tfidf",
        index=False
    )

    # Full vocabulary
    results_df.to_excel(
        writer,
        sheet_name="vocabulary",
        index=False
    )

print(f"\nSaved to: {OUTPUT_XLSX}")
print("  - top_50_words: frequency + TF-IDF together")
print("  - top_50_tfidf: highest TF-IDF words")
