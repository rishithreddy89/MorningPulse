import { createFileRoute } from "@tanstack/react-router";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card } from "@/components/ui/card";
import { SectionHeader } from "@/components/dashboard/Primitives";
import { useDashboardData } from "@/lib/dashboard-context";
import { normalizeDirection } from "@/lib/dashboard-data";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/trends")({
  head: () => ({
    meta: [
      { title: "Trends — MorningPulse AI" },
      { name: "description", content: "Emerging trends across the market." },
    ],
  }),
  component: TrendsRoute,
});

function TrendsRoute() {
  return (
    <DashboardLayout>
      <TrendsContent />
    </DashboardLayout>
  );
}

function TrendsContent() {
  const { digest, isLoading, error } = useDashboardData();
  const trends = digest?.trends ?? [];

  return (
    <div className="mx-auto max-w-6xl">
      <SectionHeader title="Trends" description="All tracked signals." />
      {isLoading && <p className="text-sm text-muted-foreground">Loading trends...</p>}

      {!isLoading && error && <p className="text-sm text-destructive">{error}</p>}

      {!isLoading && !error && trends.length === 0 && (
        <p className="text-sm text-muted-foreground">No data yet. Click refresh.</p>
      )}

      {!isLoading && !error && trends.length > 0 && (
        <div className="grid gap-3 sm:grid-cols-2">
          {trends.map((trend, index) => {
            const direction = normalizeDirection(trend.direction);
            return (
              <Card key={`${trend.name}-${index}`} className="border-border p-5 shadow-none">
                <div className="flex items-start justify-between gap-3">
                  <h3 className="text-sm font-semibold">{trend.name}</h3>
                  <span
                    className={cn(
                      "text-xs font-medium tabular-nums",
                      direction === "increasing"
                        ? "text-success"
                        : direction === "decreasing"
                          ? "text-destructive"
                          : "text-muted-foreground",
                    )}
                  >
                    {direction}
                  </span>
                </div>
                <p className="mt-1.5 text-sm text-muted-foreground">{trend.explanation}</p>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
