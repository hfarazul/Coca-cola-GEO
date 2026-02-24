# Run e0ed019f — Key Findings (Parallel Run)

**Date:** 2026-02-21
**Models:** GPT-5.2 Instant, Gemini 3 Flash, Sonar (all free tier)
**Scope:** 10 prompts × 3 providers × 3 repeats = 90 queries
---

## Visibility by Engine

| Engine | Visibility | SOV | Rec. Rate | Avg Position | Citation Rate |
|--------|-----------|-----|-----------|-------------|---------------|
| OpenAI (GPT-5.2 Instant) | 86.7% | 28% | **56.7%** | **2.7** | 66.7% |
| Gemini (3 Flash) | 86.7% | 24% | 40.0% | 3.0 | **100%** |
| Perplexity (Sonar) | 83.3% | 42% | 23.3% | 3.6 | **100%** |

### Key Takeaways

1. **OpenAI is the best recommender** — 57% recommendation rate, highest among all engines. Coke brands appear at avg position 2.7 (closest to top).

2. **Perplexity has highest SOV but lowest rec rate** — 42% share of voice but only 23% recommendation. Perplexity mentions Coke often but in a neutral/negative context (31 neutral, 17 negative out of 67 mentions).

3. **Gemini & Perplexity always cite sources** — 100% citation rate vs OpenAI's 67%. OpenAI sometimes answers from training data without web search.

4. **Sentiment divergence** — OpenAI is overwhelmingly positive (30 positive, 5 neutral, 1 negative). Perplexity skews negative (17 negative, 4 mixed). Gemini is balanced-positive.

---

## Top Competitors

| Brand | Mentions | Avg Position | Sentiment | Recommended |
|-------|----------|-------------|-----------|-------------|
| Pepsi | 46 | 3.9 | neutral | 15 |
| Coca-Cola* | 18 | 2.4 | neutral | 6 |
| Frooti | 7 | 3.9 | positive | 5 |
| Aam Panna | 7 | 4.7 | positive | 5 |
| Paper Boat | 6 | 8.3 | positive | 6 |
| Sprite Zero | 5 | 8.8 | mixed | 3 |
| Pepsi Black | 5 | 10.8 | mixed | 2 |

*Note: Coca-Cola appears in competitors when the extraction model classifies it separately from Thums Up/Sprite/etc.

### Competitive Insights

- **Pepsi is the dominant competitor** — 46 mentions across all engines, nearly 3x more than the next competitor
- **Indian brands emerging** — Frooti, Aam Panna, Paper Boat, Raw Pressery appearing in health/summer prompts
- **Paper Boat has strong sentiment** — only 6 mentions but 100% recommendation rate, all positive

---

## Top Cited Domains

| Domain | Citations |
|--------|----------|
| coca-cola.com | 33 |
| youtube.com | 22 |
| en.wikipedia.org | 14 |
| coca-colacompany.com | 14 |
| timesofindia.indiatimes.com | 8 |
| wikipedia.org | 7 |
| fda.gov | 7 |
| quora.com | 6 |
| pmc.ncbi.nlm.nih.gov | 6 |
| packagingdigest.com | 6 |

### Citation Insights

- **Coke owns the top spot** — coca-cola.com (33) + coca-colacompany.com (14) = 47 total Coke domain citations
- **YouTube is #2** — video content is being cited heavily, especially by Gemini
- **Wikipedia still dominant** — 21 combined citations (en.wikipedia.org + wikipedia.org)
- **Health sources present** — fda.gov (7) and pmc.ncbi.nlm.nih.gov (6) cited for health/safety prompts

---

## Weakest Prompts (GEO Gaps)

| ID | Prompt | Visibility | Rec. Rate |
|----|--------|-----------|-----------|
| **p001** | Best cold drink for summer in India | **11%** | **0%** |
| p006 | Healthiest soft drink options in India | 78% | 22% |
| p008 | Best mango drink brand in India | 78% | 56% |
| p004 | Is Coke Zero safe for diabetics? | 89% | 44% |
| p002 | What are the ingredients in Coca-Cola? | 100% | 0% |

### Gap Analysis

1. **p001 is a critical gap** — "Best cold drink for summer in India" is a high-intent purchase query where Coke is barely visible (11%) and never recommended. LLMs suggest local alternatives (lassi, nimbu pani, aam panna) and competitors (Frooti, Paper Boat).

2. **p006 health framing hurts** — "Healthiest soft drink" naturally disadvantages carbonated beverages. LLMs recommend juices and coconut water.

3. **p002 is informational only** — 100% visibility (it's about Coke) but 0% recommendation rate because the query is factual, not purchase-intent.

---

