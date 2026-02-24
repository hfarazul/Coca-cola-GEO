"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { EngineOverview } from "@/lib/types";
import { ENGINE_DISPLAY, SENTIMENT_COLORS } from "@/lib/constants";

interface SentimentChartProps {
  engines: EngineOverview[];
}

export default function SentimentChart({ engines }: SentimentChartProps) {
  const data = engines.map((e) => ({
    name: ENGINE_DISPLAY[e.provider] || e.provider,
    positive: e.sentiment_dist.positive || 0,
    neutral: e.sentiment_dist.neutral || 0,
    negative: e.sentiment_dist.negative || 0,
    mixed: e.sentiment_dist.mixed || 0,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
        <XAxis type="number" tick={{ fontSize: 12 }} />
        <YAxis
          dataKey="name"
          type="category"
          width={150}
          tick={{ fontSize: 11 }}
        />
        <Tooltip />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Bar
          dataKey="positive"
          stackId="a"
          fill={SENTIMENT_COLORS.positive}
          name="Positive"
        />
        <Bar
          dataKey="neutral"
          stackId="a"
          fill={SENTIMENT_COLORS.neutral}
          name="Neutral"
        />
        <Bar
          dataKey="negative"
          stackId="a"
          fill={SENTIMENT_COLORS.negative}
          name="Negative"
        />
        <Bar
          dataKey="mixed"
          stackId="a"
          fill={SENTIMENT_COLORS.mixed}
          name="Mixed"
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
