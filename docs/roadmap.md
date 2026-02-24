# Coca-Cola India GEO Tracker — Roadmap

**Created:** 2026-02-21
**Status:** MVP complete (Steps 0-7). Planning next phases.

---

## What's Built (MVP)

- 3 engines: OpenAI GPT-4o, Gemini Flash, Perplexity Sonar Pro
- 10 seed prompts, 3 repeats, brand extraction, citation normalization
- SQLite storage, CLI reporting, CSV export, cost tracking
- First run complete: 90 queries, $0.46, key findings documented

---

## Phase 2A: Prompt Expansion (10 → 50)

### Current Gaps

| Gap | Issue |
|-----|-------|
| Only 5 categories | Missing: occasions, price/value, regional, defensive, e-commerce |
| Only 3 Coke brands tested | Missing: Sprite, Fanta, Maaza, Limca, Kinley, Minute Maid |
| Only 3 brand-agnostic prompts | Should be ~40% (20 of 50) — these are highest signal |
| Zero gen_z persona | Critical demographic for Coke India |
| No negative/defensive prompts | "is Coke bad for health" — must track what engines say |
| No long-tail queries | Real users ask longer, more specific questions |
| No query variations | Should have 5-8 variations per primary query per iPullRank |

### Target: 50 Prompts

| Bucket | Count | Examples |
|--------|-------|---------|
| Brand-agnostic purchase | 8 | "best cold drink India", "soft drinks for party", "cheapest cola brand" |
| Brand-specific product | 6 | "Sprite vs 7Up", "Limca flavors", "Kinley water quality" |
| Health & safety | 8 | "is Coke bad for kids", "sugar in Indian soft drinks", "Coke Zero vs Diet Coke" |
| Comparison | 6 | "Thums Up vs Pepsi vs Campa", "Maaza vs Frooti vs Slice" |
| Occasions & usage | 5 | "drinks for Indian wedding", "best mixer for rum India" |
| Regional & cultural | 5 | "popular drinks in South India", "festival drinks Tamil Nadu" |
| Sustainability & CSR | 4 | "plastic waste Coca-Cola India", "Coke water replenishment" |
| Defensive / reputation | 4 | "Coca-Cola controversies India", "pesticides in soft drinks India" |
| E-commerce & availability | 4 | "order Thums Up online", "Coke offers on Blinkit" |

### New Personas Needed
- gen_z (18-24, social media native, trend-driven)
- parent (buying for family/kids)
- event_planner (weddings, parties, corporate events)
- bartender (mixers, cocktails)
- rural_consumer (value-focused, regional preference)

---

## Phase 2B: Multi-Model Testing (Same Provider, Different Models)

### Why This Matters

We've only been testing premium/paid models. But most Indian users are on free tiers — they see completely different models and potentially different brand recommendations.

**Research evidence:**
- "Sonar Pro returns ~2x more citations than standard Sonar" — same provider, 2x difference in citation behavior
- Our own data: OpenAI GPT-4o had only 10% citation rate — GPT-4o-mini (free tier) may have 0%
- Enterprise tools like Profound capture "real user-facing front-end data" across 400M+ conversations to account for this
- Non-determinism research (NAACL 2025): different model sizes = different training data, reasoning depth, and web search behavior

### Model Matrix

| Provider | Free Tier (majority of users) | Paid Tier (current testing) | Reasoning Tier |
|----------|------------------------------|----------------------------|----------------|
| OpenAI | GPT-4o-mini | GPT-4o | o3-mini / o3 |
| Google | Gemini 2.0 Flash | Gemini 2.5 Pro | Gemini 2.5 Flash Thinking |
| Perplexity | Sonar | Sonar Pro | Sonar Reasoning |

### What to Measure (Free vs Paid)
- Does GPT-4o-mini even trigger web search? (Suspected: less often → fewer citations)
- Does Gemini Flash give different brand recommendations than Gemini Pro?
- Does Sonar vs Sonar Pro change which brands get cited? (Research says 2x citation difference)
- Do reasoning models (o3, Sonar Reasoning) give more nuanced answers that mention more brands?

### Implementation
- Add model parameter to each provider's config
- Run same prompt set across free-tier and paid-tier models
- Compare: visibility, SOV, citation rate, sentiment, recommendation rate
- Report which model tier is most/least favorable to Coke

### Cost Impact
- GPT-4o-mini is ~10x cheaper than GPT-4o → negligible cost increase
- Gemini Flash is already cheapest → Pro costs ~10x more
- Sonar (free-tier model) is cheaper than Sonar Pro
- Net: testing free-tier models is actually cheaper than current testing

### Business Impact
- If Coke visibility is 80% on GPT-4o but 40% on GPT-4o-mini, the real-world visibility is closer to 40% (most users are on free)
- Optimization priorities change: maybe health prompts are fine on paid tier but terrible on free tier
- This gap is what enterprise tools like Profound charge $399-1,499/mo to surface

---

## Phase 2C: More Engines (New Providers)

| Engine | Method | Why | Effort | Cost Impact |
|--------|--------|-----|--------|-------------|
| Claude (Anthropic) | Web search tool via API | Major AI player, different citation behavior | Medium — new provider | ~$0.02/query |
| Google AI Overviews | SerpAPI scraping | What users actually see in Google Search | Medium — REST API | ~$0.015/query |
| DeepSeek | OpenAI-compatible API | Growing market share, especially in Asia | Low — similar to Perplexity | ~$0.01/query |
| Grok (xAI) | API | Twitter/X integration, real-time data | Low | TBD |
| Google AI Mode | SerpAPI (google_ai_mode) | India was first international market | Medium | ~$0.015/query |

**Priority:** Claude + Google AI Overviews first (highest user reach in India).

---

## Phase 2C: Vernacular / Indian Language Prompts

### Why This Matters
- No existing GEO tool tracks Hindi/Tamil/Telugu AI citations
- Indian queries are 2-5x longer than English, often Hinglish
- Gemini supports 9 Indian languages, ChatGPT supports 12+
- This is the core differentiation vs off-the-shelf tools

### Implementation
- Translate top 20 prompts into Hindi, Tamil, Telugu
- Test if engines respond in the same language or switch to English
- Track if citations change (local-language sources vs English sources)
- Compare brand visibility: does Coke do better or worse in Hindi queries?

### Example Hindi Prompts
- "भारत में सबसे अच्छा कोल्ड ड्रिंक कौन सा है" (Best cold drink in India)
- "थम्स अप और पेप्सी में कौन बेहतर है" (Thums Up vs Pepsi which is better)
- "कोका कोला में कितनी चीनी होती है" (How much sugar in Coca-Cola)

---

## Phase 3: Optimization Loop (Measure → Act → Re-measure)

### 3A: Content Gap Analysis Engine

Build an automated system that:
1. Takes the weakest prompts from our report
2. Analyzes what content currently exists on coca-cola.com for those queries
3. Identifies what's missing (FAQ pages, product pages, blog posts)
4. Generates content briefs with specific recommendations
5. After content is published, re-runs the same prompts to measure impact

**Example workflow:**
- p001 "Best cold drink for summer in India" → 0% Coke visibility
- Audit coca-cola.com: no page addresses "summer drinks India"
- Brief: Create `/in/en/summer-drinks` page with FAQPage schema listing Coke products alongside traditional drinks
- Publish → wait 2-4 weeks → re-run p001 → measure visibility change

### 3B: Schema Markup Audit & Recommendations

Automated audit of coca-cola.com/in and competitor sites:
- Check for FAQPage, Product, NutritionInformation, Organization schema
- Score each page's "AI readiness" (structured data, content freshness, passage quality)
- Generate specific schema markup snippets to add
- Per our research: FAQPage = 13x odds ratio, Product = 4x, only 12.4% of sites use structured data

### 3C: Citation Source Optimization

Track and improve which domains cite Coke:
- Map current citation sources (coca-cola.com is #1, good)
- Identify authoritative domains that cite competitors but not Coke
- Build outreach list: Wikipedia editors, health sites, recipe sites
- Track coca-cola.com crawl patterns by AI bots (GPTBot, ClaudeBot, Google-Extended)

---

## Phase 4: Competitive Intelligence

### 4A: Dedicated Competitor Tracking

Run the same prompt set but score for competitors:
- Pepsi portfolio: Pepsi, Mountain Dew, Mirinda, 7Up, Slice, Tropicana
- Campa Cola (Reliance) — fastest growing disruptor
- Frooti / Parle Agro — dominating mango category in AI
- Regional: Bovonto, Lahori Zeera, Paper Boat

Track their visibility, SOV, sentiment, citation sources over time.

### 4B: New Entrant Alerts

Automated detection of new brands appearing in AI responses:
- Flag any brand name in responses that's not in our known dictionaries
- Example: "BROBOND" appeared in Gemini responses — new entrant we should track
- Weekly alert: "New brand detected: X appeared in Y% of responses"

---

## Phase 5: Dashboard & Automation

### 5A: Scheduled Runs
- APScheduler or cron for weekly automated runs
- Slack/email alerts on significant changes (>5% visibility swing)
- Delta tracking: compare each run to previous, surface trends

### 5B: Dashboard
- Streamlit or Metabase connected to SQLite/PostgreSQL
- Real-time visibility scores, trend charts, competitor comparison
- Drill-down: click a prompt → see all 3 engine responses side by side
- Export to PowerPoint for stakeholder presentations

### 5C: Database Migration
- SQLite → PostgreSQL for concurrent access and dashboard performance
- Add data retention policies (keep raw responses for 90 days, aggregates forever)

---

## Phase 6: Advanced Analytics

### 6A: Temporal Analysis
- Track how responses change week-over-week for the same prompt
- Detect seasonality (do summer drink queries favor Coke more in March-June?)
- Measure content freshness impact (how quickly do new Coke pages get cited?)

### 6B: Response Clustering
- Cluster similar responses across engines using embeddings
- Identify "response archetypes" — what are the 5-6 standard ways engines answer cola queries?
- Track which archetype each engine gravitates toward over time

### 6C: Predictive Citation Modeling
- Build a model predicting citation probability based on:
  - Domain authority, content freshness, schema markup, word count, passage structure
- Use this to prioritize which pages to optimize
- Similar to AthenaHQ's ACE (Athena Citation Engine) but custom for Coke India

---

## Phase 7: E-Commerce & Quick Commerce Integration

### 7A: PDP Monitoring
Track how Coke products appear on Indian quick commerce platforms:
- Blinkit, Zepto, Swiggy Instamart, Amazon Fresh, BigBasket, JioMart
- Monitor: pricing, stock availability, ratings, search ranking, ad placements
- Use Apify actors (Blinkit scraper exists) + custom scrapers

### 7B: AI Shopping Citations
- ChatGPT Shopping is live — track if/when Coke products appear in shopping recommendations
- Google AI Overviews show product carousels for shopping queries
- Map the path: AI query → citation → click → PDP → purchase

---

## Effort & Cost Estimates

| Phase | Effort | Monthly Cost | Timeline |
|-------|--------|-------------|----------|
| 2A: 50 prompts | 1 day | ~$10/run | Week 1 |
| 2B: Multi-model (free vs paid tiers) | 1 day | ~$5/run (free models are cheaper) | Week 1-2 |
| 2C: +2 engines (Claude, AIO) | 2-3 days | +$5-10/run | Week 2 |
| 2D: Hindi/Tamil/Telugu | 2 days | +$10/run | Week 3 |
| 3A: Content gap engine | 1 week | Minimal | Month 2 |
| 3B: Schema audit | 3 days | Minimal | Month 2 |
| 4A: Competitor tracking | 2 days | +$5/run | Month 2 |
| 5A: Weekly automation | 1 day | ~$40-80/mo | Month 2 |
| 5B: Dashboard | 1 week | Hosting costs | Month 3 |
| 6: Advanced analytics | 2 weeks | Minimal | Month 3-4 |
| 7: E-commerce integration | 2 weeks | Apify ~$50/mo | Month 4 |

**Total projected cost at full scale:** $150-400/month







 The high-impact stuff most people miss

  1. Optimization loop (not just measurement)
  Right now we only measure. The real value is: measure → identify gaps → create/fix content → re-measure → prove impact. Example:
  p001 "best cold drink in India" has 0% Coke visibility. We could build a system that automatically audits coca-cola.com for what's
  missing and generates content briefs.

  2. Defensive monitoring
  We're not tracking what engines say when someone asks "is Coca-Cola harmful" or "Coke pesticide controversy India". These queries
  exist and the responses could be damaging. Need to know what's being said before it becomes a problem.

  3. Vernacular is the real moat
  No GEO tool tracks Hindi/Tamil/Telugu citations. Gemini supports 9 Indian languages. Do engines say different things about Coke in
  Hindi vs English? Almost certainly yes — and nobody is measuring it.

  4. Citation source optimization
  coca-cola.com is already the #1 cited domain (good). But defendourhealth.org got 8 citations and likely frames Coke negatively. We
  can map which authoritative domains cite competitors but not Coke, and build a targeted content/outreach strategy.

  5. Competitor early warning
  Campa Cola (Reliance) and Lahori Zeera are showing up in AI responses. We can auto-detect new brands appearing in responses that
  aren't in our dictionary — catching disruptors early.

  6. E-commerce crossover
  ChatGPT Shopping is live. Track if "order cold drinks online" queries lead to Coke products or competitors on Blinkit/Zepto.
