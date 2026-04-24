import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { fetchDates, fetchDigest, fetchDigestByDate, triggerPipelineRun } from "@/lib/api";
import type { DashboardDigest } from "@/lib/dashboard-data";

const BACKEND_UNREACHABLE_MESSAGE = "Backend not reachable. Start server.";
const REFRESH_POLL_INTERVAL_MS = 10000;
const REFRESH_MAX_ATTEMPTS = 9;

interface DashboardContextValue {
  digest: DashboardDigest | null;
  dates: string[];
  selectedDate: string | null;
  isLoading: boolean;
  isRefreshing: boolean;
  error: string | null;
  selectDate: (date: string) => Promise<void>;
  refreshDigest: () => Promise<boolean>;
}

const DashboardContext = createContext<DashboardContextValue | undefined>(undefined);

function wait(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

export function DashboardDataProvider({ children }: { children: ReactNode }) {
  const [digest, setDigest] = useState<DashboardDigest | null>(null);
  const [dates, setDates] = useState<string[]>([]);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectDate = async (date: string) => {
    setSelectedDate(date);
    setIsLoading(true);

    const data = await fetchDigestByDate(date);
    if (data) {
      setDigest(data);
      setError(null);
    } else {
      setDigest(null);
      setError("No data yet. Click refresh.");
    }

    setIsLoading(false);
  };

  const refreshDigest = async (): Promise<boolean> => {
    const started = await triggerPipelineRun();
    if (!started) {
      setError(BACKEND_UNREACHABLE_MESSAGE);
      return false;
    }

    setIsRefreshing(true);

    const previousGeneratedAt = digest?.generated_at ?? "";

    for (let attempt = 0; attempt < REFRESH_MAX_ATTEMPTS; attempt += 1) {
      await wait(REFRESH_POLL_INTERVAL_MS);
      const nextDigest = selectedDate ? await fetchDigestByDate(selectedDate) : await fetchDigest();
      if (!nextDigest) {
        continue;
      }

      const hasNewDigest = (nextDigest.generated_at ?? "") !== previousGeneratedAt;
      if (!hasNewDigest) {
        continue;
      }

      setDigest(nextDigest);
      setSelectedDate(nextDigest.date);
      setError(null);
      const nextDates = await fetchDates();
      if (nextDates) {
        setDates(nextDates);
      }
      setIsRefreshing(false);
      return true;
    }

    setIsRefreshing(false);
    setError("No data yet. Click refresh.");
    return false;
  };

  useEffect(() => {
    const initialize = async () => {
      setIsLoading(true);

      const [latestDigest, availableDates] = await Promise.all([fetchDigest(), fetchDates()]);
      if (availableDates) {
        setDates(availableDates);
      }

      if (latestDigest) {
        setDigest(latestDigest);
        setSelectedDate(latestDigest.date);
        setError(null);
        setIsLoading(false);
        return;
      }

      if (availableDates && availableDates.length > 0) {
        const newestDate = availableDates[0];
        const historicalDigest = await fetchDigestByDate(newestDate);
        if (historicalDigest) {
          setDigest(historicalDigest);
          setSelectedDate(historicalDigest.date);
          setError(null);
          setIsLoading(false);
          return;
        }
      }

      setDigest(null);
      if (availableDates === null) {
        setError(BACKEND_UNREACHABLE_MESSAGE);
      } else {
        setError(null);
      }
      setIsLoading(false);
    };

    void initialize();
  }, []);

  return (
    <DashboardContext.Provider
      value={{
        digest,
        dates,
        selectedDate,
        isLoading,
        isRefreshing,
        error,
        selectDate,
        refreshDigest,
      }}
    >
      {children}
    </DashboardContext.Provider>
  );
}

export function useDashboardData(): DashboardContextValue {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error("useDashboardData must be used within DashboardDataProvider");
  }
  return context;
}
