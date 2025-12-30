const API_BASE = "http://localhost:8000/api";

export type Ticker = { symbol: string; name: string };
export type TickerSummary = {
  symbol: string;
  asof_date: string;
  summary: string;
  bullets: string[];
  confidence: number;
};

export async function listTickers(): Promise<Ticker[]> {
  const r = await fetch(`${API_BASE}/tickers`);
  if (!r.ok) throw new Error("Failed to fetch tickers");
  return r.json();
}

export async function getTickerSummary(symbol: string, asofDate?: string): Promise<TickerSummary> {
  const q = asofDate ? `?asof_date=${encodeURIComponent(asofDate)}` : "";
  const r = await fetch(`${API_BASE}/tickers/${symbol}/summary${q}`);
  if (!r.ok) throw new Error("Summary not found. Run daily job first.");
  return r.json();
}

export async function runDaily(): Promise<{ fetched_reports: number; mentions_created: number; summaries_created: number; asof_date: string }> {
  const r = await fetch(`${API_BASE}/tickers/run-daily`, { method: "POST" });
  if (!r.ok) throw new Error("Failed to run daily pipeline");
  return r.json();
}
