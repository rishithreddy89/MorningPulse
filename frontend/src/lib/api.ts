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
