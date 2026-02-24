"use client";

interface KpiCardProps {
  label: string;
  value: string;
  subtitle?: string;
  color?: string;
}

function KpiCard({ label, value, subtitle, color = "#1E1E1E" }: KpiCardProps) {
  return (
    <div className="kpi-card">
      <p className="text-sm text-gray-500 font-medium uppercase tracking-wide mb-1">
        {label}
      </p>
      <p className="text-4xl font-bold" style={{ color }}>
        {value}
      </p>
      {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
    </div>
  );
}

interface KpiCardsProps {
  visibility: number;
  recRate: number;
  sov: number;
}

export default function KpiCards({
  visibility,
  recRate,
  sov,
}: KpiCardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <KpiCard
        label="Overall Visibility"
        value={`${visibility.toFixed(1)}%`}
        subtitle="% of AI responses mentioning any Coke brand"
        color="#F40009"
      />
      <KpiCard
        label="Recommendation Rate"
        value={`${recRate.toFixed(1)}%`}
        subtitle="% of responses recommending Coke as top choice"
        color="#CC0000"
      />
      <KpiCard
        label="Share of Voice"
        value={`${sov.toFixed(1)}%`}
        subtitle="Coke mentions vs all brand mentions"
        color="#1E1E1E"
      />
    </div>
  );
}
