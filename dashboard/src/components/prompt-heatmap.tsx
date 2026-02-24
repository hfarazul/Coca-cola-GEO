"use client";

import { PromptData } from "@/lib/types";
import { ENGINE_DISPLAY } from "@/lib/constants";

function getHeatColor(value: number): string {
  if (value <= 50) {
    const ratio = value / 50;
    const r = 239;
    const g = Math.round(68 + ratio * (179 - 68));
    const b = Math.round(68 + ratio * (0 - 68));
    return `rgb(${r}, ${g}, ${b})`;
  } else {
    const ratio = (value - 50) / 50;
    const r = Math.round(239 - ratio * (239 - 34));
    const g = Math.round(179 + ratio * (197 - 179));
    const b = Math.round(0 + ratio * (94 - 0));
    return `rgb(${r}, ${g}, ${b})`;
  }
}

function getTextColor(value: number): string {
  return value > 30 && value < 70 ? "#1E1E1E" : "#FFFFFF";
}

interface PromptHeatmapProps {
  data: PromptData[];
  metric: "visibility_pct" | "rec_pct";
  title: string;
}

export default function PromptHeatmap({
  data,
  metric,
  title,
}: PromptHeatmapProps) {
  const promptIds = [...new Set(data.map((d) => d.prompt_id))];
  const providers = [...new Set(data.map((d) => d.provider))];

  const lookup: Record<string, number> = {};
  for (const d of data) {
    lookup[`${d.prompt_id}-${d.provider}`] = d[metric];
  }

  const promptText: Record<string, string> = {};
  for (const d of data) {
    promptText[d.prompt_id] = d.prompt_text;
  }

  return (
    <div>
      <h4 className="text-sm font-semibold text-gray-600 mb-2">{title}</h4>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr>
              <th className="text-left py-1 px-2 text-[11px] text-gray-500 font-medium" style={{ width: "45%" }}>
                Prompt
              </th>
              {providers.map((p) => (
                <th
                  key={p}
                  className="text-center py-1 px-1 text-[11px] text-gray-500 font-medium w-[100px]"
                >
                  {ENGINE_DISPLAY[p]?.split(" ")[0] || p}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {promptIds.map((pid) => (
              <tr key={pid}>
                <td
                  className="py-0.5 px-2 text-[12px] text-gray-700"
                  title={promptText[pid]}
                >
                  <span className="font-mono text-gray-400 mr-1">{pid}</span>
                  {promptText[pid]}
                </td>
                {providers.map((prov) => {
                  const val = lookup[`${pid}-${prov}`] ?? 0;
                  return (
                    <td key={prov} className="py-0.5 px-1">
                      <div
                        className="flex items-center justify-center font-semibold text-[12px] rounded h-7"
                        style={{
                          backgroundColor: getHeatColor(val),
                          color: getTextColor(val),
                        }}
                        title={`${promptText[pid]} - ${ENGINE_DISPLAY[prov]}: ${val}%`}
                      >
                        {val}%
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
