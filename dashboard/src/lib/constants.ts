export const ENGINE_DISPLAY: Record<string, string> = {
  openai: "ChatGPT (GPT-5.2)",
  gemini: "Gemini (3 Flash)",
  perplexity: "Perplexity (Sonar)",
};

export const ENGINE_COLORS: Record<string, string> = {
  openai: "#10A37F",
  gemini: "#4285F4",
  perplexity: "#20808D",
};

export const SENTIMENT_COLORS: Record<string, string> = {
  positive: "#22C55E",
  neutral: "#6B7280",
  negative: "#EF4444",
  mixed: "#F59E0B",
};

export const COKE_COLORS = {
  red: "#F40009",
  darkRed: "#CC0000",
  black: "#1E1E1E",
  white: "#FFFFFF",
  gold: "#C4A35A",
  lightGray: "#F5F5F5",
};

// Pricing per 1M tokens (Feb 2026)
export const PRICING: Record<string, { input: number; output: number }> = {
  "gpt-5": { input: 2.0, output: 8.0 },
  "gpt-4o": { input: 2.5, output: 10.0 },
  "gpt-4o-mini": { input: 0.15, output: 0.6 },
  "gemini-3-flash-preview": { input: 0.1, output: 0.4 },
  "gemini-2.0-flash": { input: 0.1, output: 0.4 },
  sonar: { input: 1.0, output: 1.0 },
  "sonar-pro": { input: 3.0, output: 15.0 },
};

export const REQUEST_FEES: Record<string, number> = {
  sonar: 5.0 / 1000,
  "sonar-pro": 5.0 / 1000,
};

export const BRAND_COLORS = [
  "#2563EB",
  "#DC2626",
  "#059669",
  "#D97706",
  "#7C3AED",
  "#DB2777",
  "#0891B2",
  "#65A30D",
  "#EA580C",
  "#4F46E5",
];

export const COKE_DOMAINS = [
  "coca-cola.com",
  "coca-colacompany.com",
  "coke.com",
  "thumsup.com",
  "sprite.com",
  "fanta.com",
  "maaza.com",
  "limca.com",
  "minutemaid.in",
];
