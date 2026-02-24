"use client";

import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ZAxis,
  Cell,
} from "recharts";
import { Competitor } from "@/lib/types";
import { BRAND_COLORS } from "@/lib/constants";

interface CompetitorBubbleProps {
  competitors: Competitor[];
}

export default function CompetitorBubble({
  competitors,
}: CompetitorBubbleProps) {
  const data = competitors.map((c, i) => ({
    x: c.avg_position,
    y: c.mention_count,
    z: Math.max(c.recommendation_count * 100, 50),
    name: c.brand,
    sentiment: c.sentiment_mode,
    recommended: c.recommendation_count,
    color: BRAND_COLORS[i % BRAND_COLORS.length],
  }));

  return (
    <div>
      <ResponsiveContainer width="100%" height={300}>
        <ScatterChart margin={{ top: 10, right: 20, bottom: 25, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
          <XAxis
            type="number"
            dataKey="x"
            name="Avg Position"
            tick={{ fontSize: 12 }}
            label={{
              value: "Avg Position (lower = better)",
              position: "bottom",
              fontSize: 11,
              fill: "#6B7280",
            }}
            reversed
          />
          <YAxis
            type="number"
            dataKey="y"
            name="Mentions"
            tick={{ fontSize: 12 }}
            label={{
              value: "Mentions",
              angle: -90,
              position: "insideLeft",
              fontSize: 11,
              fill: "#6B7280",
            }}
          />
          <ZAxis type="number" dataKey="z" range={[40, 400]} />
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null;
              const d = payload[0].payload;
              return (
                <div className="bg-white p-3 rounded-lg shadow-lg border text-sm">
                  <p className="font-bold">{d.name}</p>
                  <p>Mentions: {d.y}</p>
                  <p>Avg Position: #{d.x}</p>
                  <p>Recommended: {d.recommended}x</p>
                  <p>Sentiment: {d.sentiment}</p>
                </div>
              );
            }}
          />
          <Scatter data={data}>
            {data.map((entry, index) => (
              <Cell
                key={index}
                fill={entry.color}
                fillOpacity={0.75}
                stroke={entry.color}
                strokeWidth={1.5}
              />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
