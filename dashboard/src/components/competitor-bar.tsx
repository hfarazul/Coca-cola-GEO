"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { Competitor } from "@/lib/types";
import { BRAND_COLORS } from "@/lib/constants";

interface CompetitorBarProps {
  competitors: Competitor[];
}

export default function CompetitorBar({ competitors }: CompetitorBarProps) {
  const data = competitors.map((c, i) => ({
    name: c.brand,
    mentions: c.mention_count,
    recommended: c.recommendation_count,
    sentiment: c.sentiment_mode,
    position: c.avg_position,
    color: BRAND_COLORS[i % BRAND_COLORS.length],
  }));

  return (
    <div>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} layout="vertical" margin={{ left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
          <XAxis type="number" tick={{ fontSize: 12 }} />
          <YAxis
            dataKey="name"
            type="category"
            width={120}
            tick={{ fontSize: 12 }}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null;
              const d = payload[0].payload;
              return (
                <div className="bg-white p-3 rounded-lg shadow-lg border text-sm">
                  <p className="font-bold">{d.name}</p>
                  <p>Mentions: {d.mentions}</p>
                  <p>Avg Position: #{d.position}</p>
                  <p>Recommended: {d.recommended}x</p>
                  <p>Sentiment: {d.sentiment}</p>
                </div>
              );
            }}
          />
          <Bar dataKey="mentions" radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell key={index} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
