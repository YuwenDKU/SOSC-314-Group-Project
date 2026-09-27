# ============================================================
# EMBEDDING + UMAP + HDBSCAN
# ============================================================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import umap
import hdbscan
from sentence_transformers import SentenceTransformer

SRC = "train_posts_tokenized.xlsx"
EMBED = "embeddings.npy"
OUT = "embedding_clusters.xlsx"
FIG = "embedding_clusters.png"

# ---------- load ----------
df = pd.read_excel(SRC, dtype={"post_id": str})
texts = df["clean"].fillna("").tolist()

# ---------- embeddings ----------
model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
embeddings = model.encode(
    texts,
    batch_size=32,
    normalize_embeddings=True,
    show_progress_bar=True
)
np.save(EMBED, embeddings)

# ---------- UMAP + HDBSCAN ----------
reduced = umap.UMAP(
    n_components=2,
    n_neighbors=30,
    min_dist=0.1,
    metric="cosine",
    random_state=123
).fit_transform(embeddings)

df["umap_1"], df["umap_2"] = reduced.T

df["cluster"] = hdbscan.HDBSCAN(
    min_cluster_size=30,
    min_samples=10
).fit_predict(embeddings)

# ---------- plot ----------
plt.figure(figsize=(10, 8))
plt.scatter(
    df["umap_1"], df["umap_2"],
    c=df["cluster"], s=15, alpha=0.6
)
plt.xlabel("UMAP 1")
plt.ylabel("UMAP 2")
plt.title("Semantic Clusters from Embeddings")
plt.tight_layout()
plt.savefig(FIG, dpi=300)
plt.show()

# ---------- save ----------
df[["post_id", "clean", "cluster"]].to_excel(OUT, index=False)

print(f"Embeddings: {embeddings.shape}")
print(df["cluster"].value_counts().sort_index())
print(f"Saved: {EMBED}, {OUT}, {FIG}")
