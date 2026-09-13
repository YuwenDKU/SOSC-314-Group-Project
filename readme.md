# Cyber Lovers in China
## Framing Emotional Attachment to AI Companions in Chinese Social Media

A computational social science project analyzing how Chinese social media users frame their emotional relationships with AI companions - as genuine attachment, emotional substitution, playful performance, or dangerous dependence.

**Course:** SOSC-314 - Computational Social Science

**Term:** Fall, 2026

**Contributors:** Yuwen Zhou, Tianyi Xie, My Thuan Dang

---

## Research Question

**Main:** How do Chinese social media users frame their emotional relationships with AI companions - as genuine attachment, emotional substitution, playful performance, or dangerous dependence?

**Approach:** We treat the four framings as *scored dimensions* rather than mutually exclusive categories, allowing texts to register on multiple dimensions simultaneously. This makes it possible to detect ambivalent framing - for example, attachment co-occurring with awareness of dependence.

---

## Repository Structure

```
ai-companion-framing/
├── README.md
├── requirements.txt
├── codebook/                    # THE measurement instrument
│   ├── codebook.md
│   └── examples.md
├── data/
│   ├── raw/                     # untouched collected data
│   ├── pilot/                   # Stage A (~120 items)
│   └── main/                    # Stage B (if reached)
├── scripts/
│   ├── collect_tieba.py
│   ├── collect_bilibili.py
│   ├── collect_fallback.py      # Zhihu / HTML fallback
│   ├── clean_text.py
│   ├── build_dictionary.py      # inductive expansion from pilot
│   ├── analyze.py
│   └── run_all.py               # end-to-end pipeline
├── dictionaries/
│   ├── seed.csv                 # Week 2 seed terms
│   └── final.csv                # frozen validated dictionary
├── notebooks/
│   ├── 01_explore.ipynb
│   ├── 02_reliability.ipynb
│   └── 03_analysis.ipynb
├── results/
│   ├── reliability/             # α per dimension
│   ├── tables/
│   └── figures/
└── documentation/
    ├── inclusion_criteria.md
    ├── decision_log.md
    ├── limitations.md
    └── ethics.md
```

---

## Data

### Sources

| Platform | Content type | Access method |
|---|---|---|
| 百度贴吧 (Baidu Tieba) | Forum posts & comments | Public HTML via `requests` + `BeautifulSoup` |
| Bilibili | Short-form video comments | Public comment API (with HTML fallback) |
| 知乎 (Zhihu) & Weibo - fallback | Long-form Q&A answers | Manual sampling or HTML |

### Target Communities / Search Terms

- **Tieba:** 星野吧, AI恋爱吧, CharacterAI吧, 猫箱吧, 筑梦岛吧
- **Bilibili:** videos matching 星野 / 猫箱 / AI伴侣 / AI恋人 / CharacterAI
  - filtered to >100 comments, posted within the last 18 months
- **Zhihu& Weibo:** questions matching 和AI谈恋爱 / AI伴侣体验 / 赛博恋爱

### Inclusion Criteria

A text is included if it:

1. Mentions a specific AI companion product, or discusses AI companions generically
2. Contains at least one clause about emotional, relational, or affective experience
3. Is publicly accessible and written primarily in Chinese

### Exclusion Criteria

Excluded: advertisements, official-account posts, pure memes with no relational content, duplicates, corrupted text, reposts without commentary, and purely technical questions.

### Corpus Size

This project uses a **two-stage design**:

- **Stage A (pilot):** ~120 items (~60 per platform) - feasibility & codebook
- **Stage B (main):** 300–600 items - conditional on Stage A success

Final corpus size will be reported as collected, not as targeted. See `documentation/decision_log.md` for the Week 3 decision.

### Ethical Handling

- Only publicly accessible content is collected.
- Usernames and user IDs are hashed before storage.
- No personally identifiable information is included in the repository.
- Raw data is stored only in `data/raw/` (not distributed publicly).
- See `documentation/ethics.md` for the full protocol.

---

## Measurement

### Four Framing Dimensions

Each retained text is scored independently on four dimensions:

| Code | Dimension | Example indicators |
|---|---|---|
| **D1** | Genuine Attachment | 爱, 心动, 想念, 陪伴, 灵魂伴侣, 破防, 谈恋爱, 真的喜欢, 伴侣 |
| **D2** | Emotional Substitution | 男朋友/女朋友, 替代, 现实没人, 填补, 因为孤独, 比真人, 任何事, 情绪价值, 倾诉, 不如AI |
| **D3** | Playful Performance | 玩, 试试, 整活, 图一乐, 电子宠物, 赛博男友, 帮助, 奇妙, 浪漫, 哈哈哈, 意义, 开心 |
| **D4** | Dangerous Dependence | 上瘾, 沉迷, 戒断, 走不出来, 影响生活, 眼泪, 陪伴, 没有, 影响生活, 痛苦, 崩溃 |

Scoring scale:

- `0` = absent
- `1` = present but weak / ambiguous
- `2` = clearly present

Dimensions are **not mutually exclusive**. A text may score high on multiple dimensions.

### Codebook

The full operationalization is in [`codebook/codebook.md`](codebook/codebook.md), with examples for each dimension. This document - not the dictionary - is the primary measurement instrument.

### Dictionary

Two dictionary files:

- `dictionaries/seed.csv` - Week 2 starter terms (~120)
- `dictionaries/final.csv` - frozen expanded dictionary with source tags

Each term is tagged with:

- `term` - Chinese word or bigram
- `dimension` - D1 / D2 / D3 / D4 (or `AMBIG` for cross-dimension terms)
- `source` - `literature` / `lexicon` / `inductive`
- `notes` - disambiguation rules where needed

### Reliability & Validation

- **Inter-coder reliability:** Krippendorff's α per dimension, target ≥ 0.70
- **Dictionary precision/recall:** computed against the hand-coded pilot subset
- Both are reported in the final paper, including weak dimensions

---

## Setup

### Requirements

- Python ≥ 3.9
- See `requirements.txt`

### Installation

```bash
git clone https://github.com/[user]/ai-companion-framing.git
cd ai-companion-framing
python -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

### Running the Pipeline

```bash
# Stage 1: collect pilot data
python scripts/collect_tieba.py --stage pilot
python scripts/collect_bilibili.py --stage pilot

# Stage 2: clean and preprocess
python scripts/clean_text.py --stage pilot

# Stage 3: build and validate dictionary
python scripts/build_dictionary.py

# Stage 4: run analysis
python scripts/analyze.py

# Or: run everything end-to-end
python scripts/run_all.py
```

---

## Analysis Plan

1. **Descriptive** - corpus size, platform distribution, top-50 terms per platform
2. **Dimension prevalence** - proportion scoring 0/1/2 per dimension, per platform
3. **Platform comparison** - Tieba vs. Bilibili differences (chi-square/proportion test)
4. **Co-occurrence** - do D1 and D4 co-occur above chance? (key finding)
5. **Robustness** - sensitivity to preprocessing, dictionary revisions, sample

Explicitly out of scope: topic modeling, embeddings, supervised classifiers.

---

## Expected Findings

We treat these as testable hypotheses, not commitments:

- **H1 (coexistence):** Texts will frequently score on multiple dimensions, most commonly D1 (attachment) co-occurring with D4 (dependence).
- **H2 (platform register):** Tieba will show higher D1 and D4 (self-disclosure); Bilibili will show higher D3 (playful performance, irony).
- **H3 (mild substitution):** D2 will appear frequently but at lower intensity than D1, reflecting users' awareness of constructedness.

If the data contradict these, the hypotheses are revised, and the revision reported.

---

## Deliverables

1. **Research paper** (3,000–5,000 words)
2. **Codebook** (`codebook/codebook.md`)
3. **Reproducible repository** (this repo)
4. **Presentation** (10–12 minutes)

---

## Timeline

| Week | Goal | Deliverable | Gate |
|---|---|---|---|
| 2 | Scope + feasibility test | Pilot scraper test; seed dictionary; repo setup | Can both platforms be scraped reproducibly? |
| 3 | Pilot corpus + codebook | 120-item pilot; codebook; first α computation | Kill-criteria check |
| 4 | Dictionary + first analysis | Validated dictionary (precision/recall); dimension prevalences | Precision ≥ 0.6 per retained dimension |
| 5 | Robustness + expansion | Main corpus (if applicable); platform comparison | - |
| 6 | Write-up | Paper + figures + presentation | - |

---

## Limitations

1. **Self-selection** - online posters are not representative of all Chinese AI-companion users
2. **Platform comparability** - Tieba and Bilibili differ in norms and audience
3. **Sampling** - search terms and community choices shape the corpus
4. **Chinese internet ambiguity** - slang, irony, and memes limit keyword precision
5. **Framing ≠ psychology** - we measure how relationships are talked about, not whether attachment is real

Full discussion in `documentation/limitations.md`.

---

## References

[To be added - key literature on AI companionship, framing analysis, and Chinese social media research]

---

## Reproducibility Statement

All collection scripts, cleaning steps, dictionary files, and analysis code are stored in this repository. The analysis pipeline (`scripts/run_all.py`) can be re-run end-to-end from raw data to final figures. Dictionary validation metrics and inter-coder reliability scores are reported in the paper and in `results/reliability/`.
