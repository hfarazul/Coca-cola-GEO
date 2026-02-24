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
  PieChart,
  Pie,
} from "recharts";
import { CitationDomain } from "@/lib/types";

interface CitationBarProps {
  domains: CitationDomain[];
}

export function CitationBar({ domains }: CitationBarProps) {
  const data = domains.slice(0, 10).map((d) => ({
    name: d.domain,
    count: d.count,
    isCoke: d.is_coke_domain,
  }));

  return (
    <ResponsiveContainer width="100%" height={350}>
      <BarChart data={data} layout="vertical" margin={{ left: 30 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
        <XAxis type="number" tick={{ fontSize: 12 }} />
        <YAxis
          dataKey="name"
          type="category"
          width={200}
          tick={{ fontSize: 11 }}
        />
        <Tooltip />
        <Bar dataKey="count" radius={[0, 4, 4, 0]} name="Citations">
          {data.map((entry, index) => (
            <Cell
              key={index}
              fill={entry.isCoke ? "#F40009" : "#D1D5DB"}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

interface CitationDonutProps {
  cokeCitations: number;
  totalCitations: number;
}

export function CitationDonut({
  cokeCitations,
  totalCitations,
}: CitationDonutProps) {
  const otherCitations = totalCitations - cokeCitations;
  const data = [
    { name: "Coke Domains", value: cokeCitations },
    { name: "Other Domains", value: otherCitations },
  ];
  const COLORS = ["#F40009", "#D1D5DB"];

  return (
    <div className="flex flex-col items-center">
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={3}
            dataKey="value"
            label={(props) => {
              const name = props.name ?? "";
              const pct = ((props.percent ?? 0) * 100).toFixed(0);
              return `${name} (${pct}%)`;
            }}
          >
            {data.map((_entry, index) => (
              <Cell key={index} fill={COLORS[index]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
      <div className="text-center mt-2">
        <p className="text-2xl font-bold" style={{ color: "#F40009" }}>
          {cokeCitations}
        </p>
        <p className="text-xs text-gray-500">
          Coke domain citations out of {totalCitations}
        </p>
      </div>
    </div>
  );
}
