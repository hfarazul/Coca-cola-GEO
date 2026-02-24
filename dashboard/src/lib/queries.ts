import { getDb } from "./db";
import { PRICING, REQUEST_FEES } from "./constants";
import type {
  Run,
  EngineOverview,
  PromptData,
  Competitor,
  CitationDomain,
  CostEntry,
  ResponseDetail,
} from "./types";
import { ENGINE_DISPLAY } from "./constants";

export function getRuns(): Run[] {
  const db = getDb();
  return db
    .prepare(
      "SELECT * FROM runs WHERE status = 'completed' ORDER BY started_at DESC"
    )
    .all() as Run[];
}

export function getLatestRunId(): string | null {
  const db = getDb();
  const row = db
    .prepare(
      "SELECT run_id FROM runs WHERE status = 'completed' ORDER BY started_at DESC LIMIT 1"
    )
    .get() as { run_id: string } | undefined;
  return row?.run_id ?? null;
}

export function getEngineOverview(runId: string): EngineOverview[] {
  const db = getDb();

  const providers = db
    .prepare("SELECT DISTINCT provider FROM responses WHERE run_id = ?")
    .all(runId) as { provider: string }[];

  return providers.map((p) => {
    const prov = p.provider;

    const total = (
      db
        .prepare(
          "SELECT COUNT(*) as cnt FROM responses WHERE provider = ? AND run_id = ?"
        )
        .get(prov, runId) as { cnt: number }
    ).cnt;

    const visible = (
      db
        .prepare(
          `SELECT COUNT(*) as cnt FROM analyses a
         JOIN responses r ON a.response_id = r.response_id
         WHERE r.provider = ? AND r.run_id = ? AND a.coke_brands_found != '[]'`
        )
        .get(prov, runId) as { cnt: number }
    ).cnt;

    const recommended = (
      db
        .prepare(
          `SELECT COUNT(*) as cnt FROM analyses a
         JOIN responses r ON a.response_id = r.response_id
         WHERE r.provider = ? AND r.run_id = ? AND a.coke_is_primary_recommendation = 1`
        )
        .get(prov, runId) as { cnt: number }
    ).cnt;

    const totalMentions = (
      db
        .prepare(
          `SELECT COUNT(*) as cnt FROM brand_mentions bm
         JOIN responses r ON bm.response_id = r.response_id
         WHERE r.provider = ? AND r.run_id = ?`
        )
        .get(prov, runId) as { cnt: number }
    ).cnt;

    const cokeMentions = (
      db
        .prepare(
          `SELECT COUNT(*) as cnt FROM brand_mentions bm
         JOIN responses r ON bm.response_id = r.response_id
         WHERE r.provider = ? AND r.run_id = ? AND bm.is_coke_brand = 1`
        )
        .get(prov, runId) as { cnt: number }
    ).cnt;

    const avgPosRow = db
      .prepare(
        `SELECT AVG(bm.position) as avg_pos FROM brand_mentions bm
       JOIN responses r ON bm.response_id = r.response_id
       WHERE r.provider = ? AND r.run_id = ? AND bm.is_coke_brand = 1`
      )
      .get(prov, runId) as { avg_pos: number | null };

    const sentRows = db
      .prepare(
        `SELECT bm.sentiment, COUNT(*) as cnt FROM brand_mentions bm
       JOIN responses r ON bm.response_id = r.response_id
       WHERE r.provider = ? AND r.run_id = ? AND bm.is_coke_brand = 1
       GROUP BY bm.sentiment`
      )
      .all(prov, runId) as { sentiment: string; cnt: number }[];

    const sentimentDist: Record<string, number> = {};
    for (const s of sentRows) {
      sentimentDist[s.sentiment] = s.cnt;
    }

    const responsesWithCitations = (
      db
        .prepare(
          `SELECT COUNT(DISTINCT c.response_id) as cnt FROM citations c
         JOIN responses r ON c.response_id = r.response_id
         WHERE r.provider = ? AND r.run_id = ?`
        )
        .get(prov, runId) as { cnt: number }
    ).cnt;

    return {
      provider: prov,
      display_name: ENGINE_DISPLAY[prov] || prov,
      total_responses: total,
      visibility: total ? Math.round((visible / total) * 1000) / 10 : 0,
      sov:
        totalMentions
          ? Math.round((cokeMentions / totalMentions) * 1000) / 10
          : 0,
      rec_rate: total ? Math.round((recommended / total) * 1000) / 10 : 0,
      avg_position: avgPosRow.avg_pos
        ? Math.round(avgPosRow.avg_pos * 10) / 10
        : null,
      sentiment_dist: sentimentDist,
      citation_rate: total
        ? Math.round((responsesWithCitations / total) * 1000) / 10
        : 0,
    };
  });
}

export function getPromptData(runId: string): PromptData[] {
  const db = getDb();
  const rows = db
    .prepare(
      `SELECT r.prompt_id, r.prompt_text, r.provider,
            COUNT(*) as total,
            SUM(CASE WHEN a.coke_brands_found != '[]' THEN 1 ELSE 0 END) as visible,
            SUM(a.coke_is_primary_recommendation) as recommended
     FROM responses r
     JOIN analyses a ON r.response_id = a.response_id
     WHERE r.run_id = ?
     GROUP BY r.prompt_id, r.provider
     ORDER BY r.prompt_id, r.provider`
    )
    .all(runId) as {
    prompt_id: string;
    prompt_text: string;
    provider: string;
    total: number;
    visible: number;
    recommended: number;
  }[];

  return rows.map((r) => ({
    prompt_id: r.prompt_id,
    prompt_text: r.prompt_text,
    provider: r.provider,
    total: r.total,
    visible: r.visible,
    recommended: r.recommended,
    visibility_pct: r.total ? Math.round((r.visible / r.total) * 100) : 0,
    rec_pct: r.total ? Math.round((r.recommended / r.total) * 100) : 0,
  }));
}

export function getCompetitors(runId: string, limit = 10): Competitor[] {
  const db = getDb();
  const rows = db
    .prepare(
      `SELECT bm.brand, COUNT(*) as cnt, AVG(bm.position) as avg_pos,
            bm.sentiment, SUM(bm.is_recommended) as rec_cnt
     FROM brand_mentions bm
     JOIN responses r ON bm.response_id = r.response_id
     WHERE r.run_id = ? AND bm.is_coke_brand = 0
     GROUP BY bm.brand
     ORDER BY cnt DESC
     LIMIT ?`
    )
    .all(runId, limit) as {
    brand: string;
    cnt: number;
    avg_pos: number;
    sentiment: string;
    rec_cnt: number;
  }[];

  return rows.map((r) => ({
    brand: r.brand,
    mention_count: r.cnt,
    avg_position: Math.round(r.avg_pos * 10) / 10,
    sentiment_mode: r.sentiment || "neutral",
    recommendation_count: r.rec_cnt || 0,
  }));
}

export function getCitations(runId: string): {
  domains: CitationDomain[];
  coke_share: { coke: number; total: number; pct: number };
} {
  const db = getDb();
  const rows = db
    .prepare(
      `SELECT c.domain, COUNT(*) as cnt, MAX(c.is_coke_domain) as is_coke
     FROM citations c
     JOIN responses r ON c.response_id = r.response_id
     WHERE r.run_id = ?
     GROUP BY c.domain
     ORDER BY cnt DESC
     LIMIT 15`
    )
    .all(runId) as { domain: string; cnt: number; is_coke: number }[];

  const totalCitations = (
    db
      .prepare(
        `SELECT COUNT(*) as cnt FROM citations c
       JOIN responses r ON c.response_id = r.response_id
       WHERE r.run_id = ?`
      )
      .get(runId) as { cnt: number }
  ).cnt;

  const cokeCitations = (
    db
      .prepare(
        `SELECT COUNT(*) as cnt FROM citations c
       JOIN responses r ON c.response_id = r.response_id
       WHERE r.run_id = ? AND c.is_coke_domain = 1`
      )
      .get(runId) as { cnt: number }
  ).cnt;

  return {
    domains: rows.map((r) => ({
      domain: r.domain,
      count: r.cnt,
      is_coke_domain: r.is_coke === 1,
    })),
    coke_share: {
      coke: cokeCitations,
      total: totalCitations,
      pct: totalCitations
        ? Math.round((cokeCitations / totalCitations) * 1000) / 10
        : 0,
    },
  };
}

export function getCosts(runId: string): {
  costs: CostEntry[];
  total: number;
} {
  const db = getDb();
  const rows = db
    .prepare(
      `SELECT provider, model, COUNT(*) as queries,
            SUM(input_tokens) as total_input,
            SUM(output_tokens) as total_output
     FROM responses WHERE run_id = ?
     GROUP BY provider, model`
    )
    .all(runId) as {
    provider: string;
    model: string;
    queries: number;
    total_input: number;
    total_output: number;
  }[];

  const costs: CostEntry[] = rows.map((r) => {
    const pricing = PRICING[r.model] || { input: 0, output: 0 };
    const inputCost = ((r.total_input || 0) / 1_000_000) * pricing.input;
    const outputCost = ((r.total_output || 0) / 1_000_000) * pricing.output;
    const requestCost = r.queries * (REQUEST_FEES[r.model] || 0);
    return {
      provider: r.provider,
      model: r.model,
      queries: r.queries,
      input_tokens: r.total_input || 0,
      output_tokens: r.total_output || 0,
      total_cost:
        Math.round((inputCost + outputCost + requestCost) * 10000) / 10000,
    };
  });

  // Extraction cost estimate
  const totalAnalyses = rows.reduce((sum, r) => sum + r.queries, 0);
  if (totalAnalyses > 0) {
    const extPricing = PRICING["gpt-4o-mini"];
    const extInput = totalAnalyses * 500;
    const extOutput = totalAnalyses * 200;
    const extCost =
      (extInput / 1_000_000) * extPricing.input +
      (extOutput / 1_000_000) * extPricing.output;
    costs.push({
      provider: "extraction",
      model: "gpt-4o-mini",
      queries: totalAnalyses,
      input_tokens: extInput,
      output_tokens: extOutput,
      total_cost: Math.round(extCost * 10000) / 10000,
    });
  }

  return {
    costs,
    total: Math.round(costs.reduce((s, c) => s + c.total_cost, 0) * 10000) / 10000,
  };
}

export function getResponses(
  runId: string,
  promptId: string,
  provider: string
): ResponseDetail[] {
  const db = getDb();
  const rows = db
    .prepare(
      `SELECT r.response_id, r.repeat_num, r.raw_text,
            a.coke_brands_found, a.competitor_brands_found,
            a.coke_is_primary_recommendation, a.response_type
     FROM responses r
     LEFT JOIN analyses a ON r.response_id = a.response_id
     WHERE r.run_id = ? AND r.prompt_id = ? AND r.provider = ?
     ORDER BY r.repeat_num`
    )
    .all(runId, promptId, provider) as {
    response_id: string;
    repeat_num: number;
    raw_text: string;
    coke_brands_found: string;
    competitor_brands_found: string;
    coke_is_primary_recommendation: number;
    response_type: string;
  }[];

  return rows.map((r) => ({
    response_id: r.response_id,
    repeat_num: r.repeat_num,
    raw_text: r.raw_text,
    coke_brands_found: JSON.parse(r.coke_brands_found || "[]"),
    competitor_brands_found: JSON.parse(r.competitor_brands_found || "[]"),
    coke_is_primary_recommendation: r.coke_is_primary_recommendation === 1,
    response_type: r.response_type,
  }));
}
