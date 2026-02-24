"use client";

import { EngineOverview } from "@/lib/types";
import { ENGINE_COLORS, SENTIMENT_COLORS } from "@/lib/constants";

function getColorClass(value: number, thresholds: [number, number] = [50, 80]) {
  if (value >= thresholds[1]) return "text-green-600 bg-green-50";
  if (value >= thresholds[0]) return "text-yellow-600 bg-yellow-50";
  return "text-red-600 bg-red-50";
}

interface EngineTableProps {
  engines: EngineOverview[];
}

export default function EngineTable({ engines }: EngineTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-3 px-4 font-semibold text-gray-600">
              Engine
            </th>
            <th className="text-center py-3 px-4 font-semibold text-gray-600">
              Visibility
            </th>
            <th className="text-center py-3 px-4 font-semibold text-gray-600">
              SOV
            </th>
            <th className="text-center py-3 px-4 font-semibold text-gray-600">
              Rec. Rate
            </th>
            <th className="text-center py-3 px-4 font-semibold text-gray-600">
              Avg Position
            </th>
            <th className="text-center py-3 px-4 font-semibold text-gray-600">
              Sentiment
            </th>
            <th className="text-center py-3 px-4 font-semibold text-gray-600">
              Citation Rate
            </th>
          </tr>
        </thead>
        <tbody>
          {engines.map((e) => {
            const totalSentiment = Object.values(e.sentiment_dist).reduce(
              (a, b) => a + b,
              0
            );
            return (
              <tr key={e.provider} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="py-3 px-4">
                  <div className="flex items-center gap-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{
                        backgroundColor:
                          ENGINE_COLORS[e.provider] || "#6B7280",
                      }}
                    />
                    <span className="font-medium">{e.display_name}</span>
                  </div>
                </td>
                <td className="text-center py-3 px-4">
                  <span
                    className={`inline-block px-2 py-1 rounded text-xs font-bold ${getColorClass(e.visibility)}`}
                  >
                    {e.visibility}%
                  </span>
                </td>
                <td className="text-center py-3 px-4">
                  <span
                    className={`inline-block px-2 py-1 rounded text-xs font-bold ${getColorClass(e.sov, [20, 35])}`}
                  >
                    {e.sov}%
                  </span>
                </td>
                <td className="text-center py-3 px-4">
                  <span
                    className={`inline-block px-2 py-1 rounded text-xs font-bold ${getColorClass(e.rec_rate, [30, 50])}`}
                  >
                    {e.rec_rate}%
                  </span>
                </td>
                <td className="text-center py-3 px-4 font-mono">
                  {e.avg_position ? `#${e.avg_position}` : "—"}
                </td>
                <td className="py-3 px-4">
                  <div className="flex gap-1 justify-center">
                    {Object.entries(e.sentiment_dist).map(([sent, count]) => (
                      <div
                        key={sent}
                        className="flex items-center gap-1 text-xs"
                        title={`${sent}: ${count}`}
                      >
                        <div
                          className="w-2 h-2 rounded-full"
                          style={{
                            backgroundColor: SENTIMENT_COLORS[sent] || "#6B7280",
                          }}
                        />
                        <span>
                          {totalSentiment
                            ? Math.round((count / totalSentiment) * 100)
                            : 0}
                          %
                        </span>
                      </div>
                    ))}
                  </div>
                </td>
                <td className="text-center py-3 px-4">
                  <span
                    className={`inline-block px-2 py-1 rounded text-xs font-bold ${getColorClass(e.citation_rate)}`}
                  >
                    {e.citation_rate}%
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
