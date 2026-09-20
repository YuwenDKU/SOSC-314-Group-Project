# ============================================================
# TIEBA SCRAPER + PREPROCESSING
# ============================================================

import os
import hashlib
import json
import random
import re
import time
from pathlib import Path

import jieba
import pandas as pd
import requests


# ---------- settings ----------

API_BASE = "http://c.tieba.baidu.com"

BASE_PARAMS = {
    "_client_id": os.environ["TIEBA_CLIENT_ID"],
    "_client_type": "2",
    "_client_version": "9.7.8.0",
    "_phone_imei": os.getenv(
        "TIEBA_IMEI",
        "000000000000000"
    ),
}

HEADERS = {
    "User-Agent": "bdtb for Android 9.7.8.0",
    "Content-Type": "application/x-www-form-urlencoded",
}

THREADS = [
    9974816726, 10285208826, 10573053816, 10850977454, 11002684373,
    9800612477, 9591629357, 9871474906, 9869009983, 10577521084,
    9437024525, 6392973752, 8570015684, 4327033981, 10337395520,
]

RAW_DIR = Path("tieba_raw")
CLEAN_DIR = Path("tieba_clean")

RAW_DIR.mkdir(exist_ok=True)
CLEAN_DIR.mkdir(exist_ok=True)

OUTPUT_XLSX = CLEAN_DIR / "tieba_posts.xlsx"

MIN_CHARS = 5
MEDIA_TYPES = {2, 3, 4, 5, 9, 10, 11, 20}
NON_CHINESE = re.compile(r"[^\u4e00-\u9fff]")

# ---------- stopwords ----------

def load_stopwords(path=Path("stopwords-zh.json")):
    if not path.exists():
        url = (
            "https://raw.githubusercontent.com/"
            "stopwords-iso/stopwords-zh/master/stopwords-zh.json"
        )
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        path.write_text(
            json.dumps(response.json(), ensure_ascii=False),
            encoding="utf-8"
        )

    return set(
        json.loads(
            path.read_text(encoding="utf-8")
        )
    )

STOPWORDS = load_stopwords()

# ---------- scraping ----------

def sign(params):
    raw = (
        "".join(
            f"{key}={params[key]}"
            for key in sorted(params)
        )
        + "tiebaclient!!!"
    )
    return hashlib.md5(
        raw.encode()
    ).hexdigest().upper()


def get_page(tid, page):
    params = {
        **BASE_PARAMS,
        "kz": str(tid),
        "pn": str(page),
        "rn": "30",
        "r": "0",
        "lz": "0",
        "st": "0",
        "z": "0",
    }
    params["sign"] = sign(params)
    response = requests.post(
        API_BASE + "/c/f/pb/page",
        data=params,
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    return response.json()

def extract_text(post):
    return "".join(
        item.get("text", "")
        for item in post.get("content") or []
        if (
            isinstance(item, dict)
            and item.get("type") not in MEDIA_TYPES
            and isinstance(item.get("text"), str)
        )
    ).strip()

def scrape_thread(tid):
    records = []
    total_pages = None
    for page in range(1, 201):
        try:
            data = get_page(tid, page)

        except Exception as e:
            print(
                f"{tid}: ERROR on page {page} ({e})"
            )
            break
        total_pages = (
            total_pages
            or data.get("page", {}).get("total_page")
        )
        posts = data.get("post_list") or []
        if not posts:
            break
        records.extend(
            {
                "thread_id": str(tid),
                "text": extract_text(post)
            }
            for post in posts
        )
        if total_pages and page >= total_pages:
            break
        time.sleep(
            random.uniform(0.5, 1.2)
        )
    return records

for tid in THREADS:
    csv_path = RAW_DIR / f"thread_{tid}.csv"
    if csv_path.exists():
        print(f"{tid}: cached")
        continue
    records = scrape_thread(tid)
    pd.DataFrame(records).to_csv(
        csv_path,
        index=False,
        encoding="utf-8-sig"
    )
    print(
        f"{tid}: scraped {len(records):,} posts"
    )

# ---------- preprocessing ----------
def clean(text):
    return NON_CHINESE.sub("", str(text)).strip()

def tokenize(text):
    return [
        token
        for token in jieba.lcut(text)
        if (
            token.strip()
            and token not in STOPWORDS
            and len(token) > 1
        )
    ]

files = list(
    RAW_DIR.glob("thread_*.csv")
)
df = pd.concat(
    [
        pd.read_csv(
            path,
            dtype={"thread_id": str}
        )
        for path in files
    ],
    ignore_index=True
)
n_raw = len(df)

df["clean"] = (
    df["text"]
    .fillna("")
    .map(clean)
)
df = df[
    df["clean"].str.len() >= MIN_CHARS
].copy()
n_len = len(df)
df["tokens"] = df["clean"].map(tokenize)
df = df[
    df["tokens"].str.len() > 0
].copy()
df["tokens_joined"] = (
    df["tokens"].str.join(" ")
)

# ---------- save to xlsx ----------
summary = (
    df.groupby("thread_id")
    .size()
    .reset_index(name="post_count")
)
with pd.ExcelWriter(
    OUTPUT_XLSX,
    engine="openpyxl"
) as writer:

    df[
        [
            "thread_id",
            "text",
            "clean",
            "tokens_joined",
        ]
    ].to_excel(
        writer,
        sheet_name="posts",
        index=False
    )
    summary.to_excel(
        writer,
        sheet_name="summary",
        index=False
    )

print(f"Raw posts:                 {n_raw:,}")
print(f"Posts after length filter: {n_len:,}")
print(f"Posts after stopwords:     {len(df):,}")
print(f"Saved to: {OUTPUT_XLSX}")
