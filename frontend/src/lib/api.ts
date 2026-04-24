import type { DashboardDigest } from "@/lib/dashboard-data";

export const API_BASE = "http://localhost:5000/api";

function isNotFound(status: number): boolean {
  return status === 404;
}

export async function fetchDigest(): Promise<DashboardDigest | null> {
  try {
    const res = await fetch(`${API_BASE}/digest`);
    if (isNotFound(res.status)) {
      return null;
    }
    if (!res.ok) {
      throw new Error("Failed to fetch digest");
    }
    return (await res.json()) as DashboardDigest;
  } catch (err) {
    console.error(err);
    return null;
  }
}

export async function fetchDigestByDate(date: string): Promise<DashboardDigest | null> {
  try {
    const res = await fetch(`${API_BASE}/digest/${date}`);
    if (isNotFound(res.status)) {
      return null;
    }
    if (!res.ok) {
      throw new Error("Failed to fetch digest by date");
    }
    return (await res.json()) as DashboardDigest;
  } catch (err) {
    console.error(err);
    return null;
  }
}

export async function fetchDates(): Promise<string[] | null> {
  try {
    const res = await fetch(`${API_BASE}/dates`);
    if (!res.ok) {
      throw new Error("Failed to fetch available dates");
    }
    const payload = (await res.json()) as { dates?: string[] };
    return payload.dates ?? [];
  } catch (err) {
    console.error(err);
    return null;
  }
}

export async function triggerPipelineRun(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/run`);
    if (!res.ok) {
      throw new Error("Failed to trigger refresh");
    }
    return true;
  } catch (err) {
    console.error(err);
    return false;
  }
}

export interface BattleCard {
  competitor_name: string;
  their_strength: string;
  their_weakness: string;
  campus_cortex_advantage: string;
  pricing_signal: string;
  user_sentiment: "positive" | "negative" | "mixed";
  sentiment_reason: string;
  sales_talking_point: string;
  threat_level: "high" | "medium" | "low";
  recommended_response: "immediate" | "monitor" | "ignore";
  response_action: string;
  sources?: Array<{ source_name: string; url: string }>;
}

export interface BattleCardsResponse {
  date: string;
  battle_cards: BattleCard[];
  total: number;
}

export async function fetchBattleCards(): Promise<BattleCardsResponse | null> {
  try {
    const res = await fetch(`${API_BASE}/battle-cards`);
    if (isNotFound(res.status)) {
      return null;
    }
    if (!res.ok) {
      throw new Error("Failed to fetch battle cards");
    }
    return (await res.json()) as BattleCardsResponse;
  } catch (err) {
    console.error(err);
    return null;
  }
}
