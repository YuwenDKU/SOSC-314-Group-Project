# ============================================================
# LDA TOPIC MODEL
# ============================================================
import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
SRC = "train_posts_tokenized.xlsx"
OUT = "train_ldatopics.xlsx"

df = pd.read_excel(SRC, dtype=str)
docs = df["tokenized"].fillna("").astype(str)
# ---------- DTM ----------
vectorizer = CountVectorizer(tokenizer=str.split,token_pattern = None, min_df=3, max_df=0.7)
dtm = vectorizer.fit_transform(docs)

print(f"Documents: {dtm.shape[0]:,}")
print(f"Terms:     {dtm.shape[1]:,}")
# ---------- LDA ----------
N_TOPICS = 6
lda = LatentDirichletAllocation(n_components=N_TOPICS,random_state=298)
lda.fit(dtm)
# ---------- top words ----------
words = vectorizer.get_feature_names_out()
topics = []
for i, topic in enumerate(lda.components_):
    top_indices = topic.argsort()[:-20 - 1:-1]
    top_words = [words[j] for j in top_indices]
    print(f"Topic {i + 1}: {', '.join(top_words)}")

    topics.append({"topic": f"Topic {i + 1}","top_words": ", ".join(top_words)})

topic_df = pd.DataFrame(topics)
topic_df.to_excel(OUT, index=False)
print(f"\nSaved: {OUT}")
