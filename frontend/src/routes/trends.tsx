import { createFileRoute } from "@tanstack/react-router";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
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

function StrengthDots({ volume }: { volume?: number }) {
  const filled = !volume ? 1 : volume >= 4 ? 5 : volume >= 2 ? 3 : 1;
  return (
    <div className="flex gap-1">
      {Array.from({ length: 5 }, (_, i) => (
        <span
          key={i}
          className={cn(
            "inline-block h-1.5 w-1.5 rounded-full",
            i < filled ? "bg-primary" : "bg-muted-foreground/30",
          )}
        />
      ))}
    </div>
  );
}

function DirectionBadge({ direction }: { direction?: string }) {
  const d = normalizeDirection(direction ?? "stable");
  return (
    <span
      className={cn(
        "text-xs font-medium",
        d === "increasing" ? "text-green-600 dark:text-green-400" :
        d === "decreasing" ? "text-destructive" :
        "text-muted-foreground",
      )}
    >
      {d === "increasing" ? "↑ Rising" : d === "decreasing" ? "↓ Falling" : "→ Stable"}
    </span>
  );
}

function TrendsContent() {
  const { digest, isLoading, error } = useDashboardData();
  const trends = digest?.emerging_tech_trends ?? [];
  const painPoints = digest?.user_pain_points ?? [];

  // Build source breakdown from trend sources
  const sourceCounts: Record<string, number> = {};
  for (const t of trends) {
    for (const s of t.sources ?? []) {
      sourceCounts[s.source_name] = (sourceCounts[s.source_name] ?? 0) + 1;
    }
  }
  const topSources = Object.entries(sourceCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6);
  const maxCount = topSources[0]?.[1] ?? 1;

  const risingCount = trends.filter(
    (t) => normalizeDirection(t.direction ?? "stable") === "increasing",
  ).length;

  return (
    <div className="mx-auto max-w-6xl space-y-10">
      <header>
        <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
          Market intelligence
        </p>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight text-foreground">Trends</h1>
      </header>

      {isLoading && (
        <Card className="border-border p-6 shadow-none">
          <p className="text-sm text-muted-foreground">Loading trends...</p>
        </Card>
      )}

      {!isLoading && error && (
        <Card className="border-border p-6 shadow-none">
          <p className="text-sm text-destructive">{error}</p>
        </Card>
      )}

      {!isLoading && !error && trends.length === 0 && (
        <Card className="border-dashed border-border p-8 text-center shadow-none">
          <p className="text-sm text-muted-foreground">
            No trend data found. Try refreshing or running the pipeline first.
          </p>
        </Card>
      )}

      {!isLoading && !error && trends.length > 0 && (
        <>
          {/* Summary metric cards */}
          <div className="grid gap-4 sm:grid-cols-3">
            {[
              { label: "Total Trends", value: trends.length },
              { label: "Rising Topics", value: risingCount },
              { label: "Sources Today", value: topSources.length },
            ].map(({ label, value }) => (
              <Card key={label} className="border-border p-5 shadow-none">
                <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  {label}
                </p>
                <p className="mt-1 text-3xl font-semibold tabular-nums text-foreground">{value}</p>
              </Card>
            ))}
          </div>

          {/* Trend cards grid */}
          <section>
            <SectionHeader
              title="Emerging Trends"
              description="Signals aggregated across forums, RFPs, and industry coverage."
            />
            <div className="grid gap-4 sm:grid-cols-2">
              {trends.map((trend, index) => (
                <Card
                  key={`${trend.trend}-${index}`}
                  className="flex flex-col border-border p-5 shadow-none transition-shadow hover:shadow-[var(--shadow-elevated)]"
                >
                  <div className="flex items-center justify-between gap-2">
                    <Badge variant="secondary" className="text-xs">
                      Emerging Trend
                    </Badge>
                    <DirectionBadge direction={trend.direction} />
                  </div>

                  <h3 className="mt-3 text-sm font-semibold text-foreground">{trend.trend}</h3>
                  <p className="mt-1.5 line-clamp-2 flex-1 text-sm text-muted-foreground">
                    {trend.explanation && trend.explanation.trim() !== ""
                      ? trend.explanation
                      : `${trend.trend} is an emerging area. See sources for details.`}
                  </p>

                  <div className="mt-4 flex items-end justify-between gap-2">
                    <div className="flex flex-wrap gap-1.5">
                      {(trend.sources ?? []).map((s, idx) =>
                        s.url && s.url !== "#" && s.url !== "N/A" ? (
                          <a
                            key={idx}
                            href={s.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="rounded-full border border-border px-2 py-0.5 text-xs text-primary hover:bg-muted"
                          >
                            {s.source_name}
                          </a>
                        ) : (
                          <span
                            key={idx}
                            className="rounded-full border border-border px-2 py-0.5 text-xs text-muted-foreground"
                          >
                            {s.source_name}
                          </span>
                        ),
                      )}
                    </div>
                    <div className="flex shrink-0 flex-col items-end gap-1">
                      <StrengthDots volume={trend.volume} />
                      {trend.volume != null && (
                        <span className="text-xs text-muted-foreground">
                          {trend.volume} posts
                        </span>
                      )}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </section>

          {/* Source breakdown */}
          {topSources.length > 0 && (
            <section>
              <SectionHeader
                title="Where trends are coming from"
                description="Source breakdown for today's signals."
              />
              <Card className="border-border p-5 shadow-none">
                <div className="space-y-3">
                  {topSources.map(([source, count]) => (
                    <div key={source} className="flex items-center gap-3">
                      <span className="w-32 shrink-0 truncate text-sm text-foreground">
                        {source}
                      </span>
                      <div className="flex-1 overflow-hidden rounded-full bg-muted">
                        <div
                          className="h-2 rounded-full bg-primary transition-all"
                          style={{ width: `${(count / maxCount) * 100}%` }}
                        />
                      </div>
                      <span className="w-16 text-right text-xs tabular-nums text-muted-foreground">
                        {count} {count === 1 ? "trend" : "trends"}
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            </section>
          )}

          {/* Pain points */}
          {painPoints.length > 0 && (
            <section>
              <SectionHeader
                title="What users are frustrated about"
                description="Pain points surfaced from community discussions."
              />
              <div className="space-y-3">
                {painPoints.slice(0, 5).map((point, index) => (
                  <Card
                    key={`${point.issue}-${index}`}
                    className="border-l-4 border-l-destructive border-border p-5 shadow-none"
                  >
                    <p className="text-sm font-medium text-foreground">{point.issue}</p>
                    <p className="mt-1 text-sm text-muted-foreground">{point.context}</p>
                    {point.sources && point.sources.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-2">
                        {point.sources.map((s, idx) =>
                          s.url && s.url !== "#" && s.url !== "N/A" ? (
                            <a
                              key={idx}
                              href={s.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-primary underline hover:text-primary/80"
                            >
                              {s.source_name}
                            </a>
                          ) : (
                            <span key={idx} className="text-xs text-muted-foreground">
                              {s.source_name}
                            </span>
                          ),
                        )}
                      </div>
                    )}
                  </Card>
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}
