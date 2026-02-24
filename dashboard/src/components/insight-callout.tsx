"use client";

interface InsightCalloutProps {
  type?: "danger" | "warning" | "success";
  children: React.ReactNode;
}

export default function InsightCallout({
  type = "danger",
  children,
}: InsightCalloutProps) {
  const styles = {
    danger: "insight-callout",
    warning: "insight-callout warning",
    success: "insight-callout success",
  };

  return <div className={styles[type]}>{children}</div>;
}
