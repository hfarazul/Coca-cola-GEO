"use client";

import { useState, useEffect } from "react";
import { PromptData, ResponseDetail } from "@/lib/types";
import { ENGINE_DISPLAY } from "@/lib/constants";

interface ResponseExplorerProps {
  promptData: PromptData[];
  runId: string;
}

export default function ResponseExplorer({
  promptData,
  runId,
}: ResponseExplorerProps) {
  const promptIds = [...new Set(promptData.map((d) => d.prompt_id))];
  const providers = [...new Set(promptData.map((d) => d.provider))];

  const promptText: Record<string, string> = {};
  for (const d of promptData) {
    promptText[d.prompt_id] = d.prompt_text;
  }

  const [selectedPrompt, setSelectedPrompt] = useState(promptIds[0] || "");
  const [selectedProvider, setSelectedProvider] = useState(providers[0] || "");
  const [responses, setResponses] = useState<ResponseDetail[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  useEffect(() => {
    if (!selectedPrompt || !selectedProvider) return;
    setLoading(true);
    fetch(
      `/api/responses?run_id=${runId}&prompt_id=${selectedPrompt}&provider=${selectedProvider}`
    )
      .then((r) => r.json())
      .then((d) => {
        setResponses(d.responses || []);
        setExpandedIdx(null);
      })
      .finally(() => setLoading(false));
  }, [selectedPrompt, selectedProvider, runId]);

  return (
    <div>
      <div className="flex gap-4 mb-4">
        <div className="flex-1">
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Prompt
          </label>
          <select
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white"
            value={selectedPrompt}
            onChange={(e) => setSelectedPrompt(e.target.value)}
          >
            {promptIds.map((pid) => (
              <option key={pid} value={pid}>
                {pid}: {promptText[pid]?.slice(0, 60)}
              </option>
            ))}
          </select>
        </div>
        <div className="w-[220px]">
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Engine
          </label>
          <select
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white"
            value={selectedProvider}
            onChange={(e) => setSelectedProvider(e.target.value)}
          >
            {providers.map((p) => (
              <option key={p} value={p}>
                {ENGINE_DISPLAY[p] || p}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading && (
        <p className="text-sm text-gray-400 animate-pulse">Loading...</p>
      )}

      <div className="space-y-3">
        {responses.map((r, idx) => (
          <div
            key={r.response_id}
            className="border border-gray-200 rounded-lg overflow-hidden"
          >
            <button
              className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 text-sm"
              onClick={() =>
                setExpandedIdx(expandedIdx === idx ? null : idx)
              }
            >
              <div className="flex items-center gap-3">
                <span className="font-mono text-xs text-gray-400">
                  Repeat #{r.repeat_num}
                </span>
                <span
                  className={`text-xs px-2 py-0.5 rounded font-medium ${
                    r.coke_is_primary_recommendation
                      ? "bg-green-100 text-green-700"
                      : "bg-gray-100 text-gray-600"
                  }`}
                >
                  {r.coke_is_primary_recommendation
                    ? "Recommends Coke"
                    : "No Recommendation"}
                </span>
                <span className="text-xs text-gray-400">{r.response_type}</span>
              </div>
              <span className="text-gray-400">
                {expandedIdx === idx ? "▲" : "▼"}
              </span>
            </button>
            {expandedIdx === idx && (
              <div className="px-4 py-3 border-t border-gray-200">
                <div className="flex gap-4 mb-3 text-xs">
                  <div>
                    <span className="text-gray-500">Coke Brands: </span>
                    <span className="font-medium text-red-600">
                      {r.coke_brands_found.length > 0
                        ? r.coke_brands_found.join(", ")
                        : "None"}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">Competitors: </span>
                    <span className="font-medium">
                      {r.competitor_brands_found.length > 0
                        ? r.competitor_brands_found.join(", ")
                        : "None"}
                    </span>
                  </div>
                </div>
                <div className="bg-gray-50 rounded p-3 text-sm leading-relaxed max-h-[300px] overflow-y-auto whitespace-pre-wrap">
                  {r.raw_text}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
