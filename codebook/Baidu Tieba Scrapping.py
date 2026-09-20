D_CODES = {
    "D1_Genuine_Attachment": ["愿意", "喜欢", "记忆", "感觉", "朋友", "情感", "真的", "觉得"],
    "D2_Emotional_Substitution": ["人类", "机器人", "社会", "情感", "工作", "用户", "没有", "只能"],
    "D3_Playful_Performance": ["游戏", "剧情", "设定", "小说", "直接", "回答", "东西", "事情", "凉凉", "哈哈"],
    "D4_Dangerous_Dependence": ["无限", "只能", "不能", "不会", "复活", "记忆", "未来", "地狱"],
}

LABELS = {
    "D1_Genuine_Attachment": "D1 Genuine attachment",
    "D2_Emotional_Substitution": "D2 Emotional substitution",
    "D3_Playful_Performance": "D3 Playful performance",
    "D4_Dangerous_Dependence": "D4 Dangerous dependence",
}


# ============================================================
# CODE POSTS
# ============================================================

for dim, keywords in D_CODES.items():

    df[dim] = df["clean"].apply(
        lambda text: int(any(keyword in text for keyword in keywords))
    )


# Number of dimensions matched
df["n_dimensions"] = df[list(D_CODES)].sum(axis=1)


# ============================================================
# MATCHED KEYWORDS
# ============================================================

for dim, keywords in D_CODES.items():

    term_col = dim + "_terms"

    df[term_col] = df["clean"].apply(
        lambda text: [
            keyword
            for keyword in keywords
            if keyword in text
        ]
    )

# ============================================================
# ONE-DIMENSION POSTS
# ============================================================

one = df[df["n_dimensions"] == 1].copy()

one["dimension"] = ""

for dim in D_CODES:
    one.loc[one[dim] == 1, "dimension"] = LABELS[dim]


one[
    [
        "thread_id",
        "text",
        "clean",
        "dimension",
        "D1_Genuine_Attachment",
        "D2_Emotional_Substitution",
        "D3_Playful_Performance",
        "D4_Dangerous_Dependence",
    ]
].to_excel(
    "one_dimension_posts.xlsx",
    index=False
)


# ============================================================
# 2+ DIMENSION POSTS
# ============================================================

multi = df[df["n_dimensions"] >= 2].copy()


# Find dimension(s) with the highest number of matched keywords
dominant_dimensions = []

for _, row in multi.iterrows():

    counts = {
        dim: len(row[dim + "_terms"])
        for dim in D_CODES
    }

    highest = max(counts.values())

    selected = [
        LABELS[dim]
        for dim, count in counts.items()
        if count == highest
    ]

    dominant_dimensions.append(" | ".join(selected))

multi["dominant_dimension"] = dominant_dimensions


# ============================================================
# CLEAN MULTI-DIMENSION OUTPUT
# ============================================================

multi[
    [
        "thread_id",
        "text",
        "clean",
        "D1_Genuine_Attachment",
        "D2_Emotional_Substitution",
        "D3_Playful_Performance",
        "D4_Dangerous_Dependence",
        "dominant_dimension",
    ]
].to_excel(
    "two_plus_dimension_posts.xlsx",
    index=False
)

# ============================================================
# SUMMARY
# ============================================================

print(f"Analyzed posts: {len(df):,}")
print(f"Posts with 1 dimension: {(df['n_dimensions'] == 1).sum():,}")
print(f"Posts with 2+ dimensions: {(df['n_dimensions'] >= 2).sum():,}")

print("Saved: one_dimension_posts.xlsx")
print("Saved: two_plus_dimension_posts.xlsx")
