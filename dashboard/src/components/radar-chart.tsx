"use client";

import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { EngineOverview } from "@/lib/types";
import { ENGINE_COLORS } from "@/lib/constants";

interface EngineRadarProps {
  engines: EngineOverview[];
}

export default function EngineRadar({ engines }: EngineRadarProps) {
  // Normalize all metrics to 0-100 scale
  // For avg_position, invert: lower is better, so 100 - (pos * 10) clamped
  const metrics = [
    "Visibility",
    "SOV",
    "Rec. Rate",
    "Citation Rate",
    "Position Score",
  ];

  const data = metrics.map((metric) => {
    const point: Record<string, string | number> = { metric };
    for (const e of engines) {
      let value: number;
      switch (metric) {
        case "Visibility":
          value = e.visibility;
          break;
        case "SOV":
          value = e.sov;
          break;
        case "Rec. Rate":
          value = e.rec_rate;
          break;
        case "Citation Rate":
          value = e.citation_rate;
          break;
        case "Position Score":
          // Invert: position 1 = 100, position 10 = 0
          value = e.avg_position
            ? Math.max(0, 100 - (e.avg_position - 1) * 11)
            : 0;
          break;
        default:
          value = 0;
      }
      point[e.provider] = Math.round(value);
    }
    return point;
  });

  return (
    <ResponsiveContainer width="100%" height={350}>
      <RadarChart data={data}>
        <PolarGrid stroke="#E5E7EB" />
        <PolarAngleAxis
          dataKey="metric"
          tick={{ fontSize: 12, fill: "#6B7280" }}
        />
        <PolarRadiusAxis
          angle={90}
          domain={[0, 100]}
          tick={{ fontSize: 10 }}
        />
        {engines.map((e) => (
          <Radar
            key={e.provider}
            name={e.display_name}
            dataKey={e.provider}
            stroke={ENGINE_COLORS[e.provider] || "#6B7280"}
            fill={ENGINE_COLORS[e.provider] || "#6B7280"}
            fillOpacity={0.15}
            strokeWidth={2}
          />
        ))}
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Tooltip />
      </RadarChart>
    </ResponsiveContainer>
  );
}
