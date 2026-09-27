# ============================================================
# CLUSTER VALIDATION
# ============================================================

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import silhouette_score
import umap

CLUSTERS = "embedding_clusters.xlsx"
EMBEDDINGS = "embeddings.npy"

df = pd.read_excel(CLUSTERS, dtype={"post_id": str})
embeddings = np.load(EMBEDDINGS)

assert len(df) == len(embeddings)
labels = df["cluster"].to_numpy()
mask = labels != -1

# ---------- within-cluster semantic similarity ----------
for c in sorted(set(labels)):
    if c == -1:
        continue

    sub = embeddings[labels == c]
    sim = cosine_similarity(sub)
    scores = sim[np.triu_indices(len(sub), k=1)]

    print(
        f"Cluster {c}: "
        f"n={len(sub)}, "
        f"mean={scores.mean():.3f}, "
        f"median={np.median(scores):.3f}")

# ---------- recreate 10D space used for clustering ----------
cluster_embedding = umap.UMAP(
    n_components=10,
    n_neighbors=30,
    min_dist=0.1,
    metric="cosine",
    random_state=123
).fit_transform(embeddings)

# ---------- silhouette ----------
score = silhouette_score(
    cluster_embedding[mask],
    labels[mask],
    metric="euclidean"
)

print(f"\nSilhouette score: {score:.3f}")
