export type Urgency = "high" | "medium" | "low";
export type Direction = "increasing" | "decreasing" | "stable";

export interface Source {
  source_name: string;
  url: string;
}

export interface Alert {
  title: string;
  summary: string;
  urgency: Urgency;
  impact_score: number;
  why_it_matters: string;
  recommended_action: string;
  source_url: string;
}

export interface Trend {
  trend: string;
  explanation: string;
  sources?: Source[];
  volume?: number;
  direction?: string;
}

export interface PainPoint {
  issue: string;
  context: string;
  sources?: Source[];
}

export interface CompetitorUpdate {
  title: string;
  description: string;
  sources?: Source[];
}

export interface DashboardDigest {
  date: string;
  competitor_updates: CompetitorUpdate[];
  user_pain_points: PainPoint[];
  emerging_tech_trends: Trend[];
}

export function normalizeUrgency(value: string): Urgency {
  if (value === "high" || value === "medium" || value === "low") {
    return value;
  }
  return "low";
}

export function normalizeDirection(value: string): Direction {
  const normalized = value?.toLowerCase();
  if (normalized === "increasing" || normalized === "decreasing" || normalized === "stable") {
    return normalized;
  }
  return "stable";
}
