import { createFileRoute } from "@tanstack/react-router";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card } from "@/components/ui/card";
import { SectionHeader } from "@/components/dashboard/Primitives";
import { trends } from "@/lib/dashboard-data";
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
      <div className="mx-auto max-w-6xl">
        <SectionHeader title="Trends" description="All tracked signals." />
        <div className="grid gap-3 sm:grid-cols-2">
          {trends.map((t) => (
            <Card key={t.id} className="border-border p-5 shadow-none">
              <div className="flex items-start justify-between gap-3">
                <h3 className="text-sm font-semibold">{t.name}</h3>
                <span
                  className={cn(
                    "text-xs font-medium tabular-nums",
                    t.direction === "increasing"
                      ? "text-success"
                      : t.direction === "decreasing"
                        ? "text-destructive"
                        : "text-muted-foreground",
                  )}
                >
                  {t.change}
                </span>
              </div>
              <p className="mt-1.5 text-sm text-muted-foreground">{t.explanation}</p>
            </Card>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
