import { useMemo, useState } from "react";
import { ArrowUpRight } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { SectionHeader, UrgencyBadge, ImpactBadge } from "@/components/dashboard/Primitives";
import {
  alerts,
  competitors,
  painPoints,
  summary,
  trends,
  type Urgency,
} from "@/lib/dashboard-data";
import { cn } from "@/lib/utils";

const filters: { label: string; value: "all" | Urgency }[] = [
  { label: "All", value: "all" },
  { label: "High", value: "high" },
  { label: "Medium", value: "medium" },
  { label: "Low", value: "low" },
];

export function DashboardPage() {
  const [filter, setFilter] = useState<"all" | Urgency>("all");

  const filteredAlerts = useMemo(
    () => (filter === "all" ? alerts : alerts.filter((a) => a.urgency === filter)),
    [filter],
  );

  return (
    <div className="mx-auto max-w-6xl space-y-10">
      <header>
        <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
          Daily brief
        </p>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight text-foreground">
          Dashboard
        </h1>
      </header>

      {/* Executive Summary */}
      <section>
        <Card className="border-border p-6 shadow-none">
          <h2 className="text-sm font-semibold tracking-tight text-foreground">
            Daily Intelligence Summary
          </h2>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{summary}</p>
        </Card>
      </section>

      {/* High Priority Alerts */}
      <section>
        <SectionHeader
          title="High Priority Alerts"
          description="Surfaced from monitored sources in the last 24 hours."
          action={
            <div className="flex items-center gap-1 rounded-md border border-border bg-card p-0.5">
              {filters.map((f) => (
                <button
                  key={f.value}
                  onClick={() => setFilter(f.value)}
                  className={cn(
                    "rounded px-2.5 py-1 text-xs font-medium transition-colors",
                    filter === f.value
                      ? "bg-accent text-accent-foreground"
                      : "text-muted-foreground hover:text-foreground",
                  )}
                >
                  {f.label}
                </button>
              ))}
            </div>
          }
        />
        <div className="space-y-3">
          {filteredAlerts.map((alert) => (
            <Card
              key={alert.id}
              className="border-border p-5 shadow-none transition-shadow hover:shadow-[var(--shadow-elevated)]"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <div className="mb-2 flex flex-wrap items-center gap-2">
                    <UrgencyBadge urgency={alert.urgency} />
                    <ImpactBadge score={alert.impact} />
                  </div>
                  <h3 className="text-sm font-semibold text-foreground">{alert.title}</h3>
                  <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">
                    {alert.summary}
                  </p>
                </div>
              </div>

              <div className="mt-4 grid gap-3 border-t border-border pt-4 sm:grid-cols-2">
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    Why it matters
                  </p>
                  <p className="mt-1 text-sm text-foreground">{alert.whyItMatters}</p>
                </div>
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    Recommended action
                  </p>
                  <p className="mt-1 text-sm font-medium text-foreground">
                    {alert.recommendedAction}
                  </p>
                </div>
              </div>

              <div className="mt-4 flex items-center justify-between">
                <a
                  href={alert.sourceUrl}
                  className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
                >
                  Source: {alert.source}
                  <ArrowUpRight className="h-3 w-3" />
                </a>
                <Button variant="ghost" size="sm" className="h-7 text-xs">
                  Mark reviewed
                </Button>
              </div>
            </Card>
          ))}
          {filteredAlerts.length === 0 && (
            <Card className="border-dashed border-border p-8 text-center shadow-none">
              <p className="text-sm text-muted-foreground">No alerts match this filter.</p>
            </Card>
          )}
        </div>
      </section>

      {/* Trends */}
      <section>
        <SectionHeader
          title="Emerging Trends"
          description="Signals aggregated across forums, RFPs, and industry coverage."
        />
        <div className="grid gap-3 sm:grid-cols-2">
          {trends.map((t) => (
            <Card
              key={t.id}
              className="border-border p-5 shadow-none transition-shadow hover:shadow-[var(--shadow-card)]"
            >
              <div className="flex items-start justify-between gap-3">
                <h3 className="text-sm font-semibold text-foreground">{t.name}</h3>
                <span
                  className={cn(
                    "shrink-0 text-xs font-medium tabular-nums",
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
              <p className="mt-3 text-xs uppercase tracking-wide text-muted-foreground">
                {t.direction}
              </p>
            </Card>
          ))}
        </div>
      </section>

      {/* Pain Points */}
      <section>
        <SectionHeader
          title="User Pain Points"
          description="Recurring frustrations from customers and prospects."
        />
        <Card className="border-border p-0 shadow-none">
          <ul className="divide-y divide-border">
            {painPoints.map((p) => (
              <li
                key={p.id}
                className="flex items-start justify-between gap-4 px-5 py-4 transition-colors hover:bg-muted/50"
              >
                <div className="min-w-0 flex-1">
                  <p className="text-sm text-foreground">{p.statement}</p>
                  <p className="mt-1 text-xs text-muted-foreground">{p.source}</p>
                </div>
                <span
                  className={cn(
                    "shrink-0 rounded-full border px-2 py-0.5 text-xs font-medium capitalize",
                    p.sentiment === "negative"
                      ? "border-destructive/30 bg-destructive/5 text-destructive"
                      : "border-border bg-muted text-muted-foreground",
                  )}
                >
                  {p.sentiment}
                </span>
              </li>
            ))}
          </ul>
        </Card>
      </section>

      {/* Competitor Updates */}
      <section>
        <SectionHeader
          title="Competitor Updates"
          description="Recent moves from companies in your tracked set."
        />
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {competitors.map((c) => (
            <Card
              key={c.id}
              className="flex flex-col border-border p-5 shadow-none transition-shadow hover:shadow-[var(--shadow-elevated)]"
            >
              <div className="flex items-center justify-between">
                <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  {c.company}
                </p>
                <ImpactBadge score={c.impact} />
              </div>
              <h3 className="mt-2 text-sm font-semibold text-foreground">{c.title}</h3>
              <p className="mt-1.5 flex-1 text-sm text-muted-foreground">{c.summary}</p>
              <div className="mt-4 border-t border-border pt-3">
                <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Recommended action
                </p>
                <p className="mt-1 text-sm font-medium text-foreground">
                  {c.recommendedAction}
                </p>
              </div>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
