# ============================================================
# CLUSTER × LDA TOPIC PROBABILITIES
# ============================================================

import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

SRC = "train_posts_tokenized.xlsx"
CLUSTERS = "embedding_clusters.xlsx"
OUT = "cluster_lda.xlsx"
N_TOPICS = 6

# ---------- load ----------
posts = pd.read_excel(SRC, dtype=str).fillna("")
clusters = pd.read_excel(CLUSTERS, dtype=str).fillna("")
posts["post_id"] = posts["post_id"].astype(str)
clusters["post_id"] = clusters["post_id"].astype(str)

# ---------- LDA ----------
vectorizer = CountVectorizer(tokenizer=str.split,token_pattern=None,min_df=3,max_df=0.8)
dtm = vectorizer.fit_transform(posts["tokenized"])
lda = LatentDirichletAllocation(n_components=N_TOPICS,random_state=298)

lda.fit(dtm)
topic_probs = lda.transform(dtm)

# ---------- merge cluster labels ----------
posts["cluster"] = clusters.set_index("post_id").loc[posts["post_id"], "cluster"].values

# ---------- average topic probabilities by cluster ----------
topic_df = pd.DataFrame(topic_probs,
                        columns=[f"Topic {i + 1}" for i in range(N_TOPICS)])

topic_df["cluster"] = posts["cluster"].values
result = (topic_df.groupby("cluster").mean().round(3))
result.insert(0,"post_count",posts["cluster"].value_counts().reindex(result.index).values)

# ---------- save ----------
result.to_excel(OUT)

print(result)
print(f"\nSaved: {OUT}")
