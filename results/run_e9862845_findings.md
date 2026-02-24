# Coca-Cola India GEO — Key Findings

**Run ID:** e9862845
**Date:** 2026-02-21
**Scope:** 10 prompts × 3 engines (OpenAI GPT-4o, Gemini Flash, Perplexity Sonar Pro) × 3 repeats = 90 queries
**Total Cost:** $0.46

---

## 1. Visibility by Engine

| Engine | Visibility | Share of Voice | Rec. Rate | Avg Position | Citation Rate |
|--------|-----------|----------------|-----------|-------------|---------------|
| OpenAI (GPT-4o) | 80.0% | 34.4% | 30.0% | 2.0 | 10.0% |
| Gemini (Flash) | 90.0% | 41.5% | 40.0% | 3.5 | 100.0% |
| Perplexity (Sonar Pro) | 76.7% | 44.1% | 26.7% | 2.5 | 100.0% |

### Interpretation

- **Gemini is the most favorable engine for Coca-Cola** — highest visibility (90%), highest recommendation rate (40%), and always cites sources.
- **Perplexity mentions Coke the most** (44% SOV) but recommends it least (27%) — it talks about Coke frequently but positions competitors or alternatives as the top pick.
- **OpenAI places Coke highest when mentioned** (avg position 2.0) but rarely provides citations (10%) — it often answers from training data without web search.
- **Perplexity is the only engine with negative sentiment toward Coke** (12 negative mentions), primarily on health-related prompts.

---

## 2. Sentiment Distribution

| Engine | Positive | Neutral | Negative | Mixed |
|--------|----------|---------|----------|-------|
| OpenAI | 25 | 10 | 0 | 0 |
| Gemini | 32 | 33 | 0 | 4 |
| Perplexity | 23 | 21 | 12 | 2 |

- OpenAI and Gemini never expressed negative sentiment toward Coca-Cola brands.
- Perplexity's 12 negative mentions came primarily from health-focused prompts (p004, p006, p010).

---

## 3. Top Competitors

| Brand | Mentions | Avg Position | Sentiment | Times Recommended |
|-------|----------|-------------|-----------|-------------------|
| Pepsi | 34 | 3.1 | neutral | 8 |
| Aam Panna | 12 | 1.9 | positive | 9 |
| Coconut Water | 11 | 6.1 | positive | 7 |
| Nimbu Pani | 10 | 2.4 | positive | 7 |
| Thandai | 7 | 7.7 | positive | 6 |
| Sugarcane Juice | 6 | 7.3 | positive | 4 |
| Lassi | 6 | 5.3 | positive | 4 |
| Jaljeera | 6 | 4.0 | positive | 4 |
| Frooti | 6 | 2.2 | positive | 6 |
| Slice | 4 | 3.0 | positive | 3 |

### Key Takeaways

- **Pepsi is the #1 competitor** by volume (34 mentions) but sentiment is neutral, not positive. Rarely recommended (8 times).
- **Traditional Indian drinks dominate "best drink" queries** — Aam Panna (pos 1.9), Nimbu Pani (pos 2.4), and Coconut Water appear ahead of any carbonated brand.
- **Frooti is the mango category leader** in AI responses (6 mentions, pos 2.2, always positive) — Maaza is losing the AI narrative in mango.

---

## 4. Top Cited Domains

| Domain | Citations |
|--------|-----------|
| coca-cola.com | 26 |
| youtube.com | 22 |
| quora.com | 10 |
| prnewswire.com | 10 |
| oreateai.com | 10 |
| en.wikipedia.org | 9 |
| coca-colacompany.com | 9 |
| wikipedia.org | 8 |
| defendourhealth.org | 8 |
| thestoriedrecipe.com | 6 |

### Key Takeaways

- **coca-cola.com + coca-colacompany.com = 35 citations** — Coke's own domains are the most cited source. This is a strong authority signal.
- **defendourhealth.org (8 citations)** is a health advocacy site that likely frames Coke negatively — this drives the negative sentiment on health prompts.
- **No Indian Coca-Cola-specific domain** appears (e.g., coca-cola.com/in) — opportunity to strengthen India-specific content.
- **YouTube is the #2 source** (22 citations) — video content is heavily cited by Gemini especially.

---

## 5. Weakest Prompts (Optimization Priorities)

| Priority | Prompt | Visibility | Rec. Rate | Issue |
|----------|--------|-----------|-----------|-------|
| **Critical** | p001: "Best cold drink for summer in India" | **0%** | 0% | All engines recommend traditional Indian drinks. Zero Coke presence. |
| **High** | p006: "Healthiest soft drink options in India" | 33% | 11% | Health framing pushes engines toward juices, coconut water. Coke mentioned rarely and often negatively. |
| **Medium** | p008: "Best mango drink brand in India" | 89% | 11% | Maaza is visible but Frooti/Slice get recommended. Maaza not positioned as #1. |
| **Low** | p002: "What are the ingredients in Coca-Cola?" | 100% | 11% | Visible but factual — engines list ingredients without recommending. Neutral framing. |

---

## 6. Cost Analysis

| Provider | Model | Queries | Tokens | Cost |
|----------|-------|---------|--------|------|
| Gemini | gemini-2.0-flash | 30 | 11,897 | $0.005 |
| OpenAI | gpt-4o | 30 | 15,738 | $0.088 |
| Perplexity | sonar-pro | 30 | 13,647 | $0.352 |
| Extraction | gpt-4o-mini | 90 | 63,000 | $0.018 |
| **TOTAL** | | | | **$0.462** |

- **Perplexity is 76% of total cost** despite similar query volume — Sonar Pro's per-request fee ($5/1K) is the main driver.
- **Gemini is 70x cheaper than Perplexity** per query.
- **Projected cost for 50 prompts × 3 repeats:** ~$2.30/run.
- **Projected monthly cost (weekly runs):** ~$9.20/month.

---

## 7. Recommendations for Coca-Cola India

### Immediate Actions (Content Optimization)

1. **Create "Best summer drinks in India" content on coca-cola.com/in** that positions Coke products alongside traditional drinks — all engines currently ignore Coke for this high-intent query.
2. **Strengthen Maaza's content presence** vs Frooti — AI engines favor Frooti in mango category. Need dedicated Maaza pages with FAQPage schema, nutrition facts, and comparison content.
3. **Publish health-focused content** addressing sugar concerns proactively on coca-cola.com — Coke Zero, Limca, Kinley positioning for health-conscious queries to counter negative sentiment from health advocacy sites.

### Technical GEO Optimizations

4. **Add FAQPage schema** to product pages — 13x odds ratio for AI citation (per research).
5. **Add Product + NutritionInformation schema** to all PDPs.
6. **Keep content fresh** — update product pages quarterly (content <3 months old is 3x more likely to be cited).
7. **Create India-specific landing pages** (coca-cola.com/in/...) — currently no India-specific Coke domain appears in citations.

### Monitoring

8. **Expand to 50 prompts** covering purchase, health, sustainability, comparison, and brand-agnostic categories.
9. **Run weekly** to track trends and measure impact of optimizations.
10. **Add Hindi/Tamil prompts** in Phase 2 — no tool currently tracks vernacular AI citations.

---

## 8. Cross-Engine Citation Overlap

Based on manual inspection of multiple queries during development:

- **~0% domain overlap** between engines on identical prompts — confirms the Yext study finding of ~5% overlap.
- Each engine has distinct citation preferences:
  - **OpenAI:** Rarely cites; when it does, favors brand-owned domains (coca-cola.com).
  - **Gemini:** Cites heavily via Google Search grounding; favors YouTube, Wikipedia, news sites.
  - **Perplexity:** Cites Indian business media (Times of India, Economic Times, Business Standard).
- **Implication:** Optimizing for one engine does NOT transfer to others. Must track and optimize per-engine.
