
# GEO Research Reference — Coca-Cola India
Last updated: 2026-02-20

---

## 1. GEO Tool Landscape (Feb 2026)

### Tier 1: Enterprise Platforms

**Profound** (tryprofound.com) — Market leader
- Coverage: 10+ engines — ChatGPT, Claude, Perplexity, Google AI Overviews, Gemini, Copilot, DeepSeek, Grok, Meta AI, Google AI Mode
- Key feature: Captures real user-facing front-end data (not simulated API calls). Conversation Explorer with 400M+ real conversations. Agent Analytics tracking how AI bots crawl your site. Shopping Insights for ChatGPT Shopping.
- Pricing: Starter $99/mo (50 prompts, ChatGPT only), Growth $399/mo (100 prompts, 3 platforms), Lite $499/mo, Agency Growth $1,499/mo, custom enterprise
- SOC 2 Type II compliant. Sequoia-backed ($35M Series B)

**Peec AI** (peec.ai)
- Coverage: ChatGPT, Gemini, Perplexity, Claude, Google AI Overviews, Copilot, DeepSeek, Grok, Llama
- Key feature: Prompt-level mention frequency, sentiment analysis, and position data at scale. Multi-country monitoring.
- Pricing: Starting at EUR 89/mo (25 prompts)
- Backed by EUR 21M Series A; 1,500+ teams

**AthenaHQ** (athenahq.ai)
- Coverage: 8+ AI platforms
- Key feature: Athena Citation Engine (ACE) — proprietary algorithm predicting citation probability. Revenue attribution via Shopify/GA4 integrations. Autonomous Action Center agents that draft optimizations.
- Pricing: Starter $295/mo (intro $95 first month), up to $499/mo; enterprise $2,000+/mo
- Y Combinator-backed, ex-Google Search/DeepMind founders

### Tier 2: SEO Platform Extensions

**Semrush AI Visibility Toolkit** (semrush.com)
- Coverage: Major AI platforms with daily updates; 220+ countries
- Key feature: Integrates with existing Semrush SEO workflow. AI Visibility Score benchmarking. Prompt Tracking with daily updates.
- Pricing: $99/mo add-on per domain; Semrush One at $199/mo bundles SEO + AI Visibility

**Ahrefs Brand Radar** (ahrefs.com/brand-radar)
- Coverage: ChatGPT, Google AI Overviews, Google AI Mode, Perplexity, Gemini, Copilot, plus YouTube, TikTok, Reddit
- Key feature: Largest prompt database (260M+ monthly prompts). Proven 0.664 correlation between branded web mentions and AI Overview visibility.
- Pricing: $199/mo per individual AI platform index, $699/mo for all 6 bundled ($828-$1,148/mo total with base Ahrefs)
- Limitation: Keyword-level tracking, not prompt-level

### Tier 3: Dedicated GEO Tools

**Otterly.AI** (otterly.ai)
- Coverage: Google AI Overviews, ChatGPT, Perplexity, Google AI Mode, Gemini, Copilot
- Key feature: Lowest-cost entry point. Automated link tracking (hyperlinked vs unlinked brand mentions). Competitive benchmarking with alerts.
- 20,000+ marketing professionals. G2, OMR, Gartner awards.
- Best for: Teams beginning their AI visibility journey

**Scrunch AI** (scrunch.com)
- Coverage: ChatGPT, Perplexity, Meta AI, Claude, Gemini, Google AI Overviews
- Key feature: Persona-driven visibility tracking. Agent Experience Platform (AXP) — machine-readable site version for AI crawlers. Citation consistency and influence scoring.
- Recognized by Gartner as top 7 AEO/GEO tool for 2026

**Goodie AI** (higoodie.com)
- Coverage: ChatGPT, Gemini, Perplexity, Claude, Copilot, DeepSeek
- Key feature: All-in-one — monitoring + optimization hub + content writer + AI crawler analytics + agentic commerce optimizer
- Pricing: Starting at $495/mo

**HubSpot AI Search Grader** (hubspot.com/aeo-grader)
- Coverage: ChatGPT, Perplexity, Gemini
- Key feature: FREE. Four-component analysis: overall grade, brand sentiment, share of voice, personalized analysis.
- Note: HubSpot acquired XFunnel (Oct 2025). XFunnel features being integrated natively. AI-driven leads convert 3x better than traditional search at HubSpot.

### Other Notable Tools

| Tool | Key Feature | Notes |
|------|------------|-------|
| LLMrefs | Keyword-based rank tracking, LLMrefs Score, weekly trends | Below avg pricing ($337/mo avg) |
| Bluefish AI | Brand protection focus, "Source Graph" visualization | $5M funded |
| Writesonic GEO Suite | Content creation + visibility tracking combined | Hybrid approach |
| GEO Metrics (formerly LLMO Metrics) | Cross-platform brand ranking | Monitoring-focused |
| Rankscale.AI | Citation source analysis — which domains drive AI answers | Dashboard-centric |
| GenRank | Timeline visualization, competitor benchmarking | Trend tracking |
| Conductor | Enterprise organic marketing + GEO benchmarking | Published landmark 2026 AEO/GEO Benchmarks Report |

---

## 2. LLM API Citation Formats (Exact Structures)

### OpenAI — Responses API with web_search_preview

```python
from openai import OpenAI
client = OpenAI()
response = client.responses.create(
    model="gpt-4o",
    tools=[{"type": "web_search_preview"}],
    input="What are the best cola brands?"
)
```

Response contains `output` array with `web_search_call` item + message with `output_text.annotations[]`:
```json
{
  "type": "url_citation",
  "start_index": 2606,
  "end_index": 2758,
  "url": "https://example.com/article",
  "title": "Article Title"
}
```
- `start_index` / `end_index` map to character positions in response text
- OpenAI requires inline citations be visible and clickable when displayed to users
- Docs: platform.openai.com/docs/guides/tools-web-search

### Claude (Anthropic) — Web Search Tool

Two distinct citation mechanisms:

**1. Document Citations** (for grounding in user-provided documents):
Set `citations.enabled=true` on documents. Returns `citations` key with page ranges (PDF) or char ranges (text). Cited text does NOT count toward output tokens.

**2. Web Search Tool** (GA since late 2025):
```python
# Enable as a tool in the request
tools=[{"type": "web_search"}]
```
Returns structured citations per content block:
```json
{
  "cited_text": "snippet up to 150 chars",
  "title": "Source Title",
  "url": "https://source.com/page"
}
```
- `cited_text`, `title`, `url` do NOT count toward input or output token usage
- No beta header required as of early 2026
- Docs: platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool

### Google Gemini — Grounding with Google Search

```python
# Pass google_search tool configuration
tools=[{"google_search": {}}]
```

Response includes `groundingMetadata`:
```json
{
  "groundingMetadata": {
    "webSearchQueries": ["search query used"],
    "searchEntryPoint": { "renderedContent": "<html>...</html>" },
    "groundingChunks": [
      { "web": { "uri": "https://source.com", "title": "Source Title" } }
    ],
    "groundingSupports": [
      {
        "segment": { "startIndex": 0, "endIndex": 150, "text": "..." },
        "groundingChunkIndices": [0, 1],
        "confidenceScores": [0.95, 0.87]
      }
    ]
  }
}
```
- `groundingChunks[]`: web sources with uri + title
- `groundingSupports[]`: maps text segments to source indices with **confidence scores** (unique to Gemini)
- `webSearchQueries`: the actual search queries the model used
- Available via Gemini API (ai.google.dev) and Vertex AI
- Docs: ai.google.dev/gemini-api/docs/google-search

### Perplexity — Sonar Pro (Native Citations)

Citations returned by default — no special config needed:
```json
{
  "id": "response-id",
  "model": "sonar-pro",
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Response text with [1] inline references [2]..."
    }
  }],
  "citations": [
    "https://source1.com/article",
    "https://source2.com/page"
  ]
}
```
- `citations[]` is a flat URL array
- Inline refs use `[1]`, `[2]` bracket notation mapping by index to citations array
- Sonar Pro returns ~2x more citations than standard Sonar
- After April 2025: citation tokens no longer billed for Sonar/Sonar Pro
- WARNING: Requesting URLs inside JSON structured output can produce hallucinated links — always use the `citations` field, not URLs from generated text
- Docs: docs.perplexity.ai/getting-started/models/models/sonar

---

## 3. Google AI Overviews — Programmatic Access

**There is NO official Google API for AI Overviews.**

### SerpAPI (Leading Option)
- **Google AI Overview API**: Scrapes AIO content from Google Search results → structured JSON with overview text, cited sources, links
- **Google AI Mode API**: Newer endpoint (`engine=google_ai_mode`) for Google AI Mode results
- Some queries need follow-up request using `page_token` for full AIO content
- Pricing: $75/mo for 5,000 searches ($0.015/query), scales to enterprise tiers
- Unused credits expire monthly

### Alternatives
| Provider | Price | Notes |
|----------|-------|-------|
| SearchAPI.io | Varies | Similar capabilities |
| Serper.dev | Varies | Lower-cost alternative |
| SearchCans | ~$0.004/query | Budget option |

### Open-Source
- SerpAPI publishes **Google AI Overview Scraper** on GitHub: github.com/serpapi/google-AI-overview-scraper
- Can be self-deployed for custom needs

---

## 4. Statistical Methods for Non-Deterministic Responses

### The Core Problem
Even with `temperature=0`, LLM APIs are NOT deterministic due to floating-point arithmetic, batching effects, and infrastructure changes. (Proven in "Evaluation of LLMs Should Not Ignore Non-Determinism", NAACL 2025)

### Approaches (Ranked by Practicality)

**1. Multiple Runs + Majority Voting (Recommended for MVP)**
- Run each prompt 3-5 times per engine
- Categorical outcomes (mentioned/not, positive/negative): majority vote
- Numerical outcomes (position): average
- Statistical significance emerges at 20-50 runs per prompt (but 3 is a practical minimum)

**2. Stable Mode Identification**
- Define a persona profile
- Run repeated inferences for that profile
- Identify the "stable mode" — most consistent high-probability answer
- Track the stable mode over time, not individual responses

**3. Bayesian Latent State Models**
- Treat true classification (e.g., "brand mentioned positively") as unobserved latent variable
- Multiple LLM ratings = noisy measurements
- Simultaneously estimate false positive/negative error rates
- Academic but powerful for enterprise deployments

**4. Method of Moments (EMNLP 2025)**
- Provides confidence intervals without excessive runs
- Paper: "A Recipe for Stochastic LLM Evaluation"
- Ref: aclanthology.org/2025.findings-emnlp.594.pdf

**5. Weighted Aggregation (LLMrefs approach)**
- Aggregate and weight results across every prompt
- Continuously check prompts to ensure statistical significance per keyword

### Practical Cost Implications
- 3 runs × 200 prompts × 5 engines = 3,000 API calls/batch
- 5 runs = 5,000 calls/batch
- At ~$0.02-0.04 avg cost per call: $60-200/batch
- Weekly cadence: $240-800/mo; Daily: $1,800-6,000/mo

---

## 5. Key Industry Studies & Benchmarks

### Yext Citation Study (Oct 2025) — 6.8M Citations, 1.6M Queries
- **Only ~5% citation overlap** across ChatGPT, Gemini, and Perplexity
- Only 12% overlap between ChatGPT, Gemini, and Copilot (separate Ahrefs study)
- 80% of AI-cited pages were ABSENT from Google's top 10 traditional results
- Citation source breakdown:
  - Websites: 44%
  - Listings: 42%
  - Reviews/Social: 8%
  - Forums (Reddit): Only 2% once location + intent filters applied
- **86% of citations come from sources brands already control** (websites, listings)
- Gemini favors websites (52.1%), OpenAI favors listings (48.7%), Perplexity diversifies
- Wikipedia dominates ChatGPT at 47.9%; Reddit more in Gemini and Perplexity

### Conductor 2026 AEO/GEO Benchmarks Report — 3.3B Sessions, 13,770 Domains
- AI referral traffic = **1.08% of all website traffic** across 10 industries
- **87.4% of AI referral traffic comes from ChatGPT**
- AI referral growing ~1% month-over-month
- **25.11% of Google searches trigger an AI Overview**
- **AI conversions are 2x higher** than traditional sources
- By industry: IT (2.8%), **Consumer Staples/CPG (1.9%)**, Healthcare (1.5%)
- **Amazon holds 17.99% AI market share** in Consumer Staples citations

### iPullRank Probabilistic AI Search Analysis
- Run each prompt 20-50 times for citation consistency
- Structure content for fragment extraction — individual sections must answer distinct sub-questions
- Map primary queries into 5-8 synthetic variations covering definitions, comparisons, costs, use cases, regulatory contexts
- Blended prompt datasets (GA4 keywords + synthetic + user-submitted) improve coverage by 42%

### Kevin Indig — State of AI Search Optimization 2026
- 24% of ChatGPT responses generated WITHOUT fetching any online content
- **Content under 3 months old is 3x more likely to be cited**
- Continuous content freshness is critical

### Ahrefs Brand Radar Research
- Proven **0.664 correlation** between branded web mentions and AI Overview visibility
- Implication: increasing brand mentions on authoritative sites directly improves AI citation likelihood

---

## 6. llms.txt — The Verdict: Largely Ineffective

### Adoption
- Out of ~300,000 domains analyzed (Originality.AI): only **10.13% have llms.txt**
- Evenly distributed across site sizes (small 9.88%, mid 10.54%, large 8.27%)
- "Scattered experiment" not a best practice

### Evidence It Doesn't Work

**Otterly.AI 90-day Experiment:**
- Out of 62,100+ AI bot visits, only **84 accessed /llms.txt** (0.1%)
- Performed **3x worse than average content pages**
- No correlation between llms.txt presence and AI crawler activity or citations
- Ref: otterly.ai/blog/the-llms-txt-experiment/

**Search Engine Journal Analysis (300K domains):**
- Statistical analysis + machine learning showed **no effect** on citation frequency
- Removing llms.txt variable from XGBoost models **improved accuracy**
- Ref: searchenginejournal.com/llms-txt-shows-no-clear-effect-on-ai-citations-based-on-300k-domains/561542/

**Google's Position:**
- Google explicitly stated it does NOT rely on llms.txt
- Compared it to the deprecated keywords meta tag

**One Anomaly:**
- OpenAI's Searchbot (not GPTBot) crawled some llms.txt files over 5,000 times at certain sites
- But this did NOT correlate with improved citations

### AI Crawler Landscape (Cloudflare 2025)
- GPTBot surged from 5% → 30% of AI crawler share (May 2024 → May 2025)
- Meta-ExternalAgent entered at 19%
- ClaudeBot dropped from 11.7% → 5.4%

### Recommendation
Implement llms.txt as a zero-cost hedge, but DO NOT rely on it. Focus instead on:
- robots.txt configuration for AI bots
- Structured content
- Schema markup

---

## 7. Schema Markup Impact on AI Citations

### Academic Evidence

**JARBMA Study (1,508 German real estate agents, ChatGPT visibility):**
| Schema Type | Visible Agents | Non-Visible | Odds Ratio |
|-------------|---------------|-------------|------------|
| FAQPage | 6.2% | 0.8% | **~13x** |
| Product | 17.2% | 1.8% | **~4x** |
| Mobile-friendly | 99.0% | 88.8% | ~5.2x |
| Avg page load | 418ms | 623ms | — |

### Industry Data
- Structured data increases AI citations by **44%** on average (Medium/Vicki Larson)
- Pages with FAQPage markup are **3.2x more likely** to appear in Google AI Overviews (Frase.io)
- ChatGPT, Claude, Perplexity, and Gemini **all actively process Schema Markup** when directly accessing content (SearchVIU tests, Oct 2025)
- Pages optimized for entity clarity + structure cited **up to 58% more often** in AI summaries (Aggarwal et al., 2024)
- JSON-LD Product schema with properly filled fields boosts AI summary appearance by **over 36%** (Stackmatix)
- **Only 12.4% of websites leverage structured data** — massive competitive advantage

### Most Effective Schema Types for FMCG/CPG (Ranked by Impact)
1. **FAQPage** — highest proven correlation (13x odds ratio)
2. **Product** (with Offer, AggregateRating) — 4x odds ratio
3. **HowTo** — strong for instructional content
4. **NutritionInformation** — nestable in Recipe/MenuItem; relevant for food/beverage (no isolated study yet)
5. **Organization/Brand** — entity authority
6. **Review/AggregateRating** — trust signal

### What Coca-Cola India Should Implement
- Product schema on every PDP with Offer, AggregateRating, NutritionInformation
- FAQPage schema answering common queries ("Is Coke Zero sugar-free?", "Thums Up ingredients")
- Organization schema with authoritative brand details
- Recipe/HowTo for cocktail mixers, cooking applications

---

## 8. India-Specific Findings

### Google AI Overviews & AI Mode in India
- **AI Overviews**: Live in India since **August 2024**. 1.5B+ users/month globally. Drives 10%+ increase in search usage for AIO-triggering queries.
- **AI Mode**: India was the **first international market** after US. Launched via Search Labs June 2025, full rollout July 2025. **Hindi support added September 2025**.
- **Search Live**: Launched India October 2025 in English + Hindi (point camera at objects → AI answers)
- **AIO trigger rate**: ~25% of queries globally. Healthcare leads at 48.75%. CPG rate not published separately.
- **Ads in AI Overviews**: Being tested for shopping queries in India — paid placement will compete with organic citations.
- **Google AI Hub**: Announced in Visakhapatnam (Oct 2025) for deploying full AI stack in India.

### Indian Language AI Capabilities
| Platform | Indian Language Support | Notes |
|----------|----------------------|-------|
| ChatGPT | 12+ Indian languages (Hindi, Tamil, Telugu, Bengali, Kannada...) | Fluency/cultural nuance inconsistent vs English. OpenAI launched IndQA benchmark. |
| Gemini | **9 languages** (Hindi, Bengali, Gujarati, Kannada, Malayalam, Marathi, Tamil, Telugu, Urdu) | Strongest position. Training for 100+ Indian languages. |
| Perplexity | Hindi + major languages | No specific Indian optimization initiative announced |

### Indian Sovereign AI Models (Track These)
- **Sarvam AI** — Vikram models (30B, 105B params), optimized for all **22 scheduled Indian languages**, voice-first. Claims to outperform DeepSeek R1 and Gemini Flash on Indian benchmarks. Sarvam Vision: 84.3% accuracy on multi-script OCR (beats ChatGPT/Gemini). Ref: sarvam.ai
- **BharatGen** — Government-led, Param 2 (17B MoE model), 22 languages, 15,000+ hours annotated voice data
- Regional: TuluAI, Aakhor AI, KashmiriGPT for underserved languages

### Implications for Vernacular Citation Tracking
- **Most GEO tools operate primarily in English** — none specifically document Hindi/Tamil/Telugu tracking accuracy
- Indian queries are **2-5x longer** than desktop English queries, often mixing Hindi + English (Hinglish)
- Increasingly voice/image search driven
- Content indexed by AI models **skews heavily Western/English**
- No tool currently tracks vernacular AI citations systematically
- A brand like Coca-Cola India needs custom prompt matrices in Hindi, Tamil, Telugu

### E-Commerce PDP Monitoring for India

**Enterprise Platforms:**
| Tool | Platforms | Key Features | Update Frequency |
|------|----------|-------------|-----------------|
| MetricsCart | Blinkit, Zepto, Swiggy Instamart, Amazon Fresh | SKU-level price/stock/discount, MAP violations, share of search, city-level | Every 10 seconds |
| 42Signals | Blinkit, Zepto, quick commerce | Ad tracking, share of search, campaign ROI, competitor intel | Real-time |
| Paxcom | Zepto, Instamart, Amazon Fresh | Availability, pricing benchmarks, compliance checks, retail media | Real-time alerts |
| GobbleCube | Quick commerce platforms | Root-cause diagnostics, competitor benchmarking by SKU | Real-time |
| Nova 9 | Blinkit, Instamart, Zepto | Omnichannel (offline+online), field team mobile app | Near real-time |

**Apify Actors Available:**
- **Blinkit Product Scraper** (apify.com/jocular_quisling/blinkit-product-scraper) — prices, stock, ratings, variants by location. Needs Apify Proxy (Blinkit blocks datacenter IPs).
- **Amazon Product Scraper** (apify.com/junglee/amazon-crawler) — works with Amazon.in; titles, prices, reviews, ratings, images, ASINs.
- **Zepto scraper** — Apify has tool for Zepto.com with location-based pricing + delivery ETAs.
- **BigBasket**: No dedicated public Apify actor. Custom scraper needed (Scrapy/Selenium).
- **JioMart**: No dedicated public Apify actor. Custom scraper needed.

**Custom Scraping Services (India-specific):**
- Actowiz Solutions — grocery price monitoring across BigBasket, Zepto, Blinkit
- FoodSpark.io — Quick Commerce Data APIs for Instamart, Zepto, Blinkit
- MobileAppScraping — API data extraction for all major platforms including DMart

---

## 9. FMCG/CPG Brands & GEO

### Current State
**No publicly documented case studies** of FMCG brands running formal GEO programs. Major CPG players invest in AI for content creation, ad generation, product innovation — not AI search visibility.

- Coca-Cola: $1.1B Microsoft cloud/AI commitment, GPT-4+DALL-E for creative, Project Fizzion
- PepsiCo: PepGenX on AWS, shortening innovation from 6+ months to 6 weeks
- Nestle: Digital twins + Tastewise. Unilever: GenAI for e-commerce product descriptions.

### Benchmarks from Other Industries
- Web dev agency: **10% of organic traffic from ChatGPT/Perplexity**, 27% converting to SQLs
- LS USA (building materials): **540% boost in Google AI Overview mentions**, 67% organic traffic increase through answer-first content + FAQ/HowTo schema
- SmartRent (prop-tech): **32% of new SQLs from AI search tools** within 6 weeks

### CPG-Specific Insight
- **Oatly** stands out for transparent sustainability disclosures + product Q&A mirroring AI conversations
- Key quote: "A generic description like 'healthy snack' is invisible to AI — you need specific, machine-readable tags like Gluten-Free, Non-GMO Project Verified, 20g Protein"

---

## 10. Cost Benchmarks & Optimization

### API Cost Per Query (Feb 2026 Pricing)
| Provider | Model | Input $/1M tokens | Output $/1M tokens | Est. cost/query |
|----------|-------|-------------------|-------------------|----------------|
| OpenAI | GPT-4o | $5.00 | $20.00 | ~$0.02-0.05 |
| Anthropic | Claude Sonnet 4 | $3.00 | $15.00 | ~$0.015-0.04 |
| Google | Gemini 2.5 Flash | $0.15 | $0.60 | ~$0.001-0.003 |
| Perplexity | Sonar Pro | $3.00 | $15.00 + request fee | ~$0.03-0.06 |
| Google AIO | SerpAPI | N/A | N/A | ~$0.015 |

### Cost Optimization Strategies
1. **Gemini Flash** as cheapest LLM option (~$0.002/query vs $0.03+ for others)
2. **Anthropic prompt caching** for repeated prompt templates
3. **OpenAI Batch API** for non-time-sensitive queries (**50% discount**)
4. **Weekly instead of daily** runs (÷7 on API costs)
5. Start with fewer prompts (50 vs 200)
6. Use **GPT-4o-mini** (~$0.001/extraction) for the extraction pass

### Scaling Scenarios
| Scenario | Prompts | Engines | Repeats | Cadence | Monthly Cost |
|----------|---------|---------|---------|---------|-------------|
| MVP (current) | 50 | 3 | 3 | On-demand | ~$5-15/run |
| Phase 2 | 100 | 5 | 3 | Weekly | ~$150-400/mo |
| Full scale | 200 | 5 | 5 | Daily | ~$1,500-3,000/mo |

---

## 11. Open-Source Tools & Repos

### GEO-Specific

**Gego** (github.com/AI2HU/gego)
- Language: Go 1.21+, GPL-3.0
- Multi-LLM scheduler with cron-based prompt scheduling
- Providers: OpenAI, Anthropic Claude, Ollama, Gemini, Perplexity Sonar
- Auto-extracts keywords from responses (no predefined list needed)
- Hybrid DB: SQLite for config, MongoDB for analytics
- REST API on port 8989
- CLI: `gego init` → `gego llm add` → `gego prompt add` → `gego schedule add` → `gego run`
- Closest to "build your own citation tracker" in OSS

**GetCito** (github.com/ai-search-guru/getcito-worlds-first-open-source-aio-aeo-or-geo-tool)
- "World's first open-source GEO tool"
- Tracks brand mentions across ChatGPT, Claude, Perplexity
- Features: Real-time citation monitoring, content gap analysis, answer-readiness scoring, AI Crawlability Clinic
- Also operates commercially at getcito.com

**GEO-optim/GEO** (github.com/GEO-optim/GEO)
- From the original Princeton/Georgia Tech/Allen Institute research paper that coined "GEO"
- Demonstrated 40% visibility improvements
- Research framework, not production tool

**AutoGEO**
- Automated framework learning what generative search engines prefer
- Up to 50% improvement in visibility

### Curated Resource Lists
- **awesome-generative-engine-optimization** (github.com/amplifying-ai/awesome-generative-engine-optimization) — 200+ tools, research papers, case studies, llms.txt resources, agentic commerce protocols
- **generative-engine-optimization-tools** (github.com/izak-fisher/generative-engine-optimization-tools) — tooling-focused list
- **Awesome-GEO** (github.com/DavidHuji/Awesome-GEO) — research-focused

### Supporting Libraries (For Building Custom)
- **LiteLLM** (github.com/BerriAI/litellm) — unified gateway for 100+ LLM providers via OpenAI-compatible interface. Proxy mode with auth, cost tracking, rate limiting. 8ms P95 at 1,000 RPS. Limitation: normalizes responses to OpenAI format, may lose provider-specific citation fields.
- **Instructor** (python.useinstructor.com) — patches LLM clients to return Pydantic models. Supports OpenAI, Anthropic, Google. Ideal for extraction pass.
- **LangChain** — `with_structured_output()` for cross-provider structured extraction. Multi-provider model abstraction.
- **LangSmith / Langfuse** — LLM observability platforms. Langfuse is open-source/self-hostable. Good for debugging prompt behavior.

---

## 12. What Worked vs What Didn't — Practitioner Consensus

### What Works
1. **Passage-level optimization** — dense retrievers evaluate fragments independently. Strong passages need standalone coherence (claim + evidence + context as self-contained units)
2. **Semantic coverage expansion** — anticipate query variations, cover terminology variants, synonyms, latent intents
3. **Authority signaling** — explicit machine-readable authorship, citations, supporting data. Domain authority alone is insufficient.
4. **Schema markup** — JSON-LD (FAQPage, Product, Article). Only 12.4% of sites do this.
5. **Content freshness** — content under 3 months old is 3x more likely to be cited
6. **Multi-platform strategy** — must track each engine separately (5% cross-platform overlap)
7. **Answer-first content structure** — direct answers upfront, then depth
8. **Blended prompt datasets** — GA4 keywords + synthetic long-tail + user-submitted prompts (42% better coverage)
9. **Persona-based sampling** — focus on specific persona profiles, track stable mode

### What Doesn't Work
1. **Single-prompt spot checks** — statistically meaningless
2. **Assuming one platform = all platforms** — 5% overlap disproves this
3. **llms.txt** — proven ineffective (0.1% crawler access rate)
4. **Reddit/forum seeding** — only 2% of citations once intent filters applied
5. **Generic keyword optimization** — LLMs favor semantic richness over keyword density
6. **Dashboards without actionable recs** — "if the tool doesn't shorten insight→execution path, you'll have another ignored dashboard by week two"
7. **Ignoring content freshness** — 3-month half-life for citation probability
8. **Overinvesting in any single strategy** — GEO requires the stack working together

### Measurement Best Practices
- Monthly or quarterly GEO audits with real screenshots
- Track AI referral traffic in GA4 as distinct channel
- Treat current tracking data as **directional**, not definitive
- 10-25 prompts surface directional trends; strategic decisions need 1,000+ samples
- The 5 metrics that matter: Citation Frequency, Brand Visibility Score, AI Share of Voice, Sentiment Analysis, LLM Conversion Rate
