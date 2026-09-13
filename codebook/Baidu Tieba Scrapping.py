# ============================================================
# PART 1 — TIEBA SCRAPER
# ============================================================

import hashlib
import json
import random
import re
import time
from pathlib import Path

import requests


# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------

API_BASE = "http://c.tieba.baidu.com"

CLIENT_VERSION = "9.7.8.0"
CLIENT_ID = "wappc_1534235498291_633"
CLIENT_TYPE = "2"
PHONE_IMEI = "000000000000000"

USER_AGENT = f"bdtb for Android {CLIENT_VERSION}"

THREADS = [
    9974816726,
    10285208826,
    10573053816,
    10850977454,
    11002684373,
    9800612477,
    9591629357,
    9871474906,
    9869009983,
    10577521084,
    9437024525,
    6392973752,
    8570015684,
    4327033981,
    10337395520,
]

RAW_DIR = Path("tieba_raw")
RAW_DIR.mkdir(exist_ok=True)


# ------------------------------------------------------------
# API
# ------------------------------------------------------------

def make_signature(params):
    raw = "".join(
        f"{k}={params[k]}"
        for k in sorted(params)
    ) + "tiebaclient!!!"

    return hashlib.md5(
        raw.encode("utf-8")
    ).hexdigest().upper()


def tieba_api(endpoint, params, timeout=20):

    params = {
        "_client_id": CLIENT_ID,
        "_client_type": CLIENT_TYPE,
        "_client_version": CLIENT_VERSION,
        "_phone_imei": PHONE_IMEI,
        **params,
    }

    params["sign"] = make_signature(params)

    response = requests.post(
        API_BASE + endpoint,
        data=params,
        headers={
            "User-Agent": USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        timeout=timeout,
    )

    response.raise_for_status()
    return response.json()


# ------------------------------------------------------------
# TEXT EXTRACTION
# ------------------------------------------------------------

def extract_text(post):

    parts = []

    for item in post.get("content", []) or []:

        if not isinstance(item, dict):
            continue

        # Ignore quoted replies, emoji, images, videos
        if item.get("type") in (2, 3, 4, 9):
            continue

        text = (
            item.get("text")
            or item.get("content")
            or ""
        )

        if isinstance(text, str):
            parts.append(text)

    return "".join(parts).strip()


# ------------------------------------------------------------
# FETCH ONE PAGE
# ------------------------------------------------------------

def get_thread_page(tid, page):

    return tieba_api(
        "/c/f/pb/page",
        {
            "kz": str(tid),
            "pn": str(page),
            "rn": "30",
            "r": "0",
            "lz": "0",
            "st": "0",
            "z": "0",
        }
    )


# ------------------------------------------------------------
# SCRAPE ONE THREAD
# ------------------------------------------------------------

def scrape_thread(tid):

    records = []
    total_pages = None

    for page in range(1, 201):

        print(
            f"Thread {tid} | page {page}",
            end="\r"
        )

        try:
            data = get_thread_page(tid, page)
        except Exception as e:
            print(
                f"\nERROR {tid}, page {page}: {e}"
            )
            break

        if total_pages is None:
            total_pages = (
                data.get("page", {})
                .get("total_page")
            )

        posts = data.get("post_list") or []

        if not posts:
            break

        for post in posts:
            records.append({
                "thread_id": str(tid),
                "text": extract_text(post),
            })

        if total_pages and page >= total_pages:
            break

        time.sleep(
            random.uniform(0.5, 1.2)
        )

    return records, total_pages


# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

for tid in THREADS:

    csv_path = RAW_DIR / f"thread_{tid}.csv"
    meta_path = RAW_DIR / f"thread_{tid}_meta.json"

    # Don't scrape again if already saved
    if csv_path.exists():
        print(f"SKIP {tid}: already cached")
        continue

    print(f"\nStarting thread {tid}")

    records, total_pages = scrape_thread(tid)

    # Save only the data we actually need
    import pandas as pd

    pd.DataFrame(records).to_csv(
        csv_path,
        index=False,
        encoding="utf-8-sig",
    )

    # Save scraping information separately
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "thread_id": str(tid),
                "total_pages_api": total_pages,
                "total_seen": len(records),
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"\nSaved {len(records):,} posts")

print("\nSCRAPING COMPLETE")

# ============================================================
# PART 2 — LOAD + CLEAN + CODE
# ============================================================

import re
from pathlib import Path

import pandas as pd


RAW_DIR = Path("tieba_raw")


# ------------------------------------------------------------
# CODING DICTIONARY
# ------------------------------------------------------------

D_CODES = {
    "D1_Genuine_Attachment": [
        "爱", "心动", "想念", "灵魂伴侣",
        "破防", "谈恋爱", "真的喜欢", "伴侣",
    ],

    "D2_Emotional_Substitution": [
        "男朋友", "女朋友", "替代", "现实没人",
        "填补", "因为孤独", "比真人", "情绪价值",
        "倾诉", "不如AI",
    ],

    "D3_Playful_Performance": [
        "玩", "试试", "整活", "图一乐",
        "电子宠物", "赛博男友", "奇妙",
        "浪漫", "哈哈哈",
    ],

    "D4_Dangerous_Dependence": [
        "上瘾", "沉迷", "戒断", "走不出来",
        "影响生活", "眼泪", "痛苦", "崩溃",
    ],
}

DIMENSION_ORDER = list(D_CODES)


# ------------------------------------------------------------
# CLEANING
# ------------------------------------------------------------

WS_RE = re.compile(r"\s+")


def clean_text(text):
    return WS_RE.sub(" ", str(text or "")).strip()


def is_junk(text):
    return (
        len(text) < 5
        or text in {"dd", "顶", "沙发", "板凳", "+1"}
    )


# ------------------------------------------------------------
# CODING
# ------------------------------------------------------------

def classify_comment(text):

    hits = {}

    for dim, keywords in D_CODES.items():

        hits[dim] = int(
            any(
                keyword.lower() in text.lower()
                for keyword in keywords
            )
        )

    matched = [
        keyword
        for dim in DIMENSION_ORDER
        for keyword in D_CODES[dim]
        if keyword.lower() in text.lower()
    ]

    hits["matched_terms"] = "|".join(
        sorted(set(matched))
    )

    hits["n_matches"] = sum(
        hits[d] for d in DIMENSION_ORDER
    )

    return hits


# ------------------------------------------------------------
# LOAD ONLY CURRENT THREADS
# ------------------------------------------------------------

files = [
    RAW_DIR / f"thread_{tid}.csv"
    for tid in THREADS
    if (RAW_DIR / f"thread_{tid}.csv").exists()
]

raw_df = pd.concat(
    [pd.read_csv(f, dtype=str) for f in files],
    ignore_index=True,
)

print(f"Raw posts: {len(raw_df):,}")


# ------------------------------------------------------------
# CLEAN
# ------------------------------------------------------------

df = raw_df.copy()

df["text"] = df["text"].map(clean_text)

df = df[
    ~df["text"].map(is_junk)
].copy()


# ------------------------------------------------------------
# CODE
# ------------------------------------------------------------

coding = pd.DataFrame(
    df["text"].map(classify_comment).tolist(),
    index=df.index,
)

df = pd.concat(
    [df, coding],
    axis=1,
)


# ------------------------------------------------------------
# KEEP CODED COMMENTS
# ------------------------------------------------------------

coded_df = (
    df[df["n_matches"] > 0]
    .drop_duplicates(subset=["thread_id", "text"])
    .reset_index(drop=True)
)


print(f"Coded comments: {len(coded_df):,}")
print(
    f"Threads with coded comments: "
    f"{coded_df['thread_id'].nunique():,}"
)

# ============================================================
# PART 3 — SUMMARY + EXPORT
# ============================================================

import json
import pandas as pd


DIM_LABELS = {
    "D1_Genuine_Attachment": "D1  Genuine attachment",
    "D2_Emotional_Substitution": "D2  Emotional substitution",
    "D3_Playful_Performance": "D3  Playful performance",
    "D4_Dangerous_Dependence": "D4  Dangerous dependence",
}


# ------------------------------------------------------------
# DIMENSION SUMMARY
# ------------------------------------------------------------

dim_sum = pd.DataFrame([
    {
        "dimension": dim,
        "n_posts": int(coded_df[dim].sum()),
        "share": coded_df[dim].mean(),
    }
    for dim in DIMENSION_ORDER
])


# ------------------------------------------------------------
# THREAD SUMMARY
# ------------------------------------------------------------

thr_sum = pd.DataFrame({
    "thread_id": [str(tid) for tid in THREADS]
})

counts = (
    coded_df
    .groupby("thread_id")
    .agg(
        coded_posts=("text", "count"),
        **{
            d: (d, "sum")
            for d in DIMENSION_ORDER
        },
    )
    .reset_index()
)

thr_sum = thr_sum.merge(
    counts,
    on="thread_id",
    how="left",
).fillna(0)

thr_sum["coded_posts"] = (
    thr_sum["coded_posts"].astype(int)
)

for dim in DIMENSION_ORDER:
    thr_sum[dim] = thr_sum[dim].astype(int)


# ------------------------------------------------------------
# FINDINGS
# ------------------------------------------------------------

findings = []

for _, row in coded_df.iterrows():

    text = row["text"].lower()

    for dim in DIMENSION_ORDER:

        if row[dim] != 1:
            continue

        for keyword in D_CODES[dim]:

            if keyword.lower() in text:

                findings.append({
                    "Thread": row["thread_id"],
                    "Dimension": DIM_LABELS[dim],
                    "Keyword": keyword,
                    "Comment": row["text"],
                })

findings_df = pd.DataFrame(findings)


# ------------------------------------------------------------
# DICTIONARY
# ------------------------------------------------------------

dictionary_df = pd.DataFrame([
    {
        "Dimension": DIM_LABELS[dim],
        "Keyword": keyword,
    }
    for dim in DIMENSION_ORDER
    for keyword in D_CODES[dim]
])


# ------------------------------------------------------------
# EXPORT
# ------------------------------------------------------------

with pd.ExcelWriter(
    "ai_companion_findings.xlsx",
    engine="openpyxl",
) as writer:

    findings_df.to_excel(
        writer,
        sheet_name="Findings",
        index=False,
    )

    dim_sum.rename(
        columns={
            "dimension": "Dimension",
            "n_posts": "Posts",
            "share": "Share",
        }
    ).to_excel(
        writer,
        sheet_name="Summary",
        index=False,
    )

    dictionary_df.to_excel(
        writer,
        sheet_name="Dictionary",
        index=False,
    )


print("Excel saved: ai_companion_findings.xlsx")

# ============================================================
# PART 4 — TWO FIGURES
# ============================================================

import matplotlib.pyplot as plt


DIM_LABELS = {
    "D1_Genuine_Attachment": "D1  Genuine attachment",
    "D2_Emotional_Substitution": "D2  Emotional substitution",
    "D3_Playful_Performance": "D3  Playful performance",
    "D4_Dangerous_Dependence": "D4  Dangerous dependence",
}

DIM_COLORS = {
    "D1_Genuine_Attachment":     "#A78BFA",
    "D2_Emotional_Substitution": "#60A5FA",
    "D3_Playful_Performance":    "#E879F9",
    "D4_Dangerous_Dependence":   "#FB7185",
}


# ============================================================
# FIGURE 1 — DIMENSION DISTRIBUTION
# ============================================================

def fig_dimension_distribution(
    dim_sum,
    path="fig1_dimension.png",
):

    if dim_sum.empty:
        print("fig1: no data")
        return

    plot_df = (
        dim_sum
        .copy()
        .sort_values("n_posts")
    )

    labels = plot_df["dimension"].map(DIM_LABELS)
    colors = plot_df["dimension"].map(DIM_COLORS)

    fig, ax = plt.subplots(figsize=(8, 4))

    bars = ax.barh(
        labels,
        plot_df["n_posts"],
        color=colors,
        height=0.6,
    )

    for bar, share in zip(bars, plot_df["share"]):
        ax.text(
            bar.get_width() + 0.3,
            bar.get_y() + bar.get_height() / 2,
            f"{share:.0%}",
            va="center",
            fontsize=10,
        )

    ax.set_xlabel("Discussion thread")
    ax.set_title(
        "How AI Companionship Is Described",
        fontsize=13,
        pad=12,
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.show()

    print(f"Saved: {path}")


# ============================================================
# FIGURE 2 — COMPOSITION PER THREAD
# ============================================================

def fig_per_thread(
    thr_sum,
    path="fig2_per_thread.png",
):

    if thr_sum.empty:
        print("fig2: no data")
        return

    plot_df = thr_sum.set_index("thread_id")

    shares = (
        plot_df[DIMENSION_ORDER]
        .div(plot_df["coded_posts"], axis=0)
        .fillna(0)
    )

    ax = shares.rename(columns=DIM_LABELS).plot(
        kind="bar",
        stacked=True,
        figsize=(10, 5),
        color=[DIM_COLORS[d] for d in DIMENSION_ORDER],
        width=0.7,
        edgecolor="white",
        linewidth=0.6,
    )

    ax.set_ylabel("Share of comments")
    ax.set_xlabel("Discussion thread")
    ax.set_title(
        "How AI-Companion Discourse Differs Across Threads",
        fontsize=13,
        pad=12,
    )

    ax.set_ylim(0, 1)
    ax.set_yticks([0, 0.25, 0.50, 0.75, 1])
    ax.set_yticklabels(
        ["0%", "25%", "50%", "75%", "100%"]
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    ax.legend(
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        frameon=False,
    )

    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.show()

    print(f"Saved: {path}")


fig_dimension_distribution(dim_sum)


fig_per_thread(thr_sum)
