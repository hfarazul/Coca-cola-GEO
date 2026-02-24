"use client";

import { useState, useEffect, useCallback } from "react";
import type {
  Run,
  EngineOverview,
  PromptData,
  Competitor,
  CitationDomain,
} from "@/lib/types";
import KpiCards from "@/components/kpi-cards";
import EngineTable from "@/components/engine-table";
import EngineRadar from "@/components/radar-chart";
import SentimentChart from "@/components/sentiment-chart";
import PromptHeatmap from "@/components/prompt-heatmap";
import CompetitorBar from "@/components/competitor-bar";
import CompetitorBubble from "@/components/competitor-bubble";
import { CitationBar, CitationDonut } from "@/components/citation-charts";
import ResponseExplorer from "@/components/response-explorer";
import InsightCallout from "@/components/insight-callout";
import { BRAND_COLORS } from "@/lib/constants";

export default function Dashboard() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [selectedRun, setSelectedRun] = useState<string>("");
  const [engines, setEngines] = useState<EngineOverview[]>([]);
  const [prompts, setPrompts] = useState<PromptData[]>([]);
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [citations, setCitations] = useState<{
    domains: CitationDomain[];
    coke_share: { coke: number; total: number; pct: number };
  }>({ domains: [], coke_share: { coke: 0, total: 0, pct: 0 } });
  const [loading, setLoading] = useState(true);

  // Load runs on mount
  useEffect(() => {
    fetch("/api/runs")
      .then((r) => r.json())
      .then((d) => {
        setRuns(d.runs || []);
        if (d.runs?.length > 0) {
          setSelectedRun(d.runs[0].run_id);
        }
      });
  }, []);

  const loadData = useCallback((runId: string) => {
    setLoading(true);
    Promise.all([
      fetch(`/api/overview?run_id=${runId}`).then((r) => r.json()),
      fetch(`/api/prompts?run_id=${runId}`).then((r) => r.json()),
      fetch(`/api/competitors?run_id=${runId}`).then((r) => r.json()),
      fetch(`/api/citations?run_id=${runId}`).then((r) => r.json()),
    ]).then(([overviewData, promptData, compData, citData]) => {
      setEngines(overviewData.engines || []);
      setPrompts(promptData.prompts || []);
      setCompetitors(compData.competitors || []);
      setCitations({
        domains: citData.domains || [],
        coke_share: citData.coke_share || { coke: 0, total: 0, pct: 0 },
      });
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    if (selectedRun) loadData(selectedRun);
  }, [selectedRun, loadData]);

  // Compute aggregate KPIs
  const avgVisibility = engines.length
    ? engines.reduce((s, e) => s + e.visibility, 0) / engines.length
    : 0;
  const avgRecRate = engines.length
    ? engines.reduce((s, e) => s + e.rec_rate, 0) / engines.length
    : 0;
  const avgSov = engines.length
    ? engines.reduce((s, e) => s + e.sov, 0) / engines.length
    : 0;

  const currentRun = runs.find((r) => r.run_id === selectedRun);

  if (loading && !engines.length) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-4 border-[#F40009] border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-gray-500">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FAFAFA]">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold" style={{ color: "#F40009" }}>
              Coca-Cola India
            </h1>
            <p className="text-sm text-gray-500">
              GEO Tracker - AI Visibility Dashboard
            </p>
          </div>
          <div className="flex items-center gap-4">
            {currentRun && (
              <div className="text-right text-xs text-gray-400">
                <p>
                  {currentRun.prompt_count} prompts x{" "}
                  {currentRun.provider_count} engines x {currentRun.repeats}{" "}
                  repeats
                </p>
                <p>
                  {new Date(currentRun.started_at).toLocaleDateString("en-IN", {
                    day: "numeric",
                    month: "short",
                    year: "numeric",
                  })}
                </p>
              </div>
            )}
            <select
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white min-w-[160px]"
              value={selectedRun}
              onChange={(e) => setSelectedRun(e.target.value)}
            >
              {runs.map((r) => (
                <option key={r.run_id} value={r.run_id}>
                  Run {r.run_id}
                </option>
              ))}
            </select>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {/* Section 1: Executive Scorecard */}
        <section>
          <h2 className="text-lg font-bold text-gray-800 mb-4">
            Executive Scorecard
          </h2>
          <KpiCards
            visibility={avgVisibility}
            recRate={avgRecRate}
            sov={avgSov}
          />
        </section>

        {/* Insight */}
        <InsightCallout type="danger">
          <p className="text-sm">
            <strong>Critical Gap:</strong> When an Indian consumer asks AI
            &quot;What&apos;s the best cold drink for summer?&quot;, Coca-Cola is
            mentioned only <strong>11% of the time</strong> and recommended{" "}
            <strong>0% of the time</strong>. AI engines suggest lassi, aam panna,
            nimbu pani, and competitors like Frooti and Paper Boat instead.
          </p>
        </InsightCallout>

        {/* Section 2: Engine Deep Dive */}
        <section className="section-card">
          <h2 className="text-lg font-bold text-gray-800 mb-4">
            Engine Comparison
          </h2>
          <EngineTable engines={engines} />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
            <div>
              <h3 className="text-sm font-semibold text-gray-600 mb-2">
                Performance Radar
              </h3>
              <EngineRadar engines={engines} />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-600 mb-2">
                Sentiment Distribution
              </h3>
              <SentimentChart engines={engines} />
            </div>
          </div>
        </section>

        {/* Insight */}
        <InsightCallout type="success">
          <p className="text-sm">
            <strong>ChatGPT is your strongest advocate</strong> - 56.7%
            recommendation rate, with 83% positive sentiment. Coke brands appear
            at avg position #2.7, closest to the top.
          </p>
        </InsightCallout>

        <InsightCallout type="warning">
          <p className="text-sm">
            <strong>Perplexity is a reputational risk</strong> - Highest SOV
            (42%) but lowest recommendation rate (23.3%). 25% of mentions are
            negative, and it often frames Coke in a health-critical context.
          </p>
        </InsightCallout>

        {/* Section 3: Prompt Performance */}
        <section className="section-card">
          <h2 className="text-lg font-bold text-gray-800 mb-4">
            Prompt-Level Performance
          </h2>
          <div className="space-y-8">
            <PromptHeatmap
              data={prompts}
              metric="visibility_pct"
              title="Visibility by Prompt & Engine"
            />
            <PromptHeatmap
              data={prompts}
              metric="rec_pct"
              title="Recommendation Rate by Prompt & Engine"
            />
          </div>
        </section>

        {/* Section 4: Competitive Landscape */}
        <section className="section-card">
          <h2 className="text-lg font-bold text-gray-800 mb-4">
            Competitive Landscape
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div>
              <h3 className="text-sm font-semibold text-gray-600 mb-2">
                Top Competitor Mentions
              </h3>
              <CompetitorBar competitors={competitors} />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-600 mb-2">
                Competitor Positioning Map
              </h3>
              <CompetitorBubble competitors={competitors} />
            </div>
          </div>
          {/* Shared legend */}
          <div className="flex flex-wrap gap-x-5 gap-y-1.5 mt-4 pt-4 border-t border-gray-100">
            {competitors.map((c, i) => (
              <div key={c.brand} className="flex items-center gap-1.5 text-[12px] text-gray-600">
                <div
                  className="w-3 h-3 rounded-sm flex-shrink-0"
                  style={{ backgroundColor: BRAND_COLORS[i % BRAND_COLORS.length] }}
                />
                <span>{c.brand}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Section 5: Citation Intelligence */}
        <section className="section-card">
          <h2 className="text-lg font-bold text-gray-800 mb-4">
            Citation Intelligence
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <h3 className="text-sm font-semibold text-gray-600 mb-2">
                Most Cited Domains
              </h3>
              <CitationBar domains={citations.domains} />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-600 mb-2">
                Coke Domain Share
              </h3>
              <CitationDonut
                cokeCitations={citations.coke_share.coke}
                totalCitations={citations.coke_share.total}
              />
            </div>
          </div>
        </section>

        {/* Section 6: Response Explorer */}
        <section className="section-card">
          <h2 className="text-lg font-bold text-gray-800 mb-4">
            Response Explorer
          </h2>
          <p className="text-sm text-gray-500 mb-4">
            Select a prompt and engine to view the actual AI responses.
          </p>
          <ResponseExplorer promptData={prompts} runId={selectedRun} />
        </section>

        {/* Footer */}
        <footer className="text-center py-8 text-xs text-gray-400">
          <p>
            Coca-Cola India GEO Tracker - Powered by Cortivo
          </p>
          {currentRun && (
            <p className="mt-1">
              Run {selectedRun} |{" "}
              {currentRun.prompt_count * currentRun.provider_count * currentRun.repeats}{" "}
              queries
            </p>
          )}
        </footer>
      </main>
    </div>
  );
}
