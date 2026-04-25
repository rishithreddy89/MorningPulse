import { createFileRoute } from "@tanstack/react-router";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { SectionHeader } from "@/components/dashboard/Primitives";
import { useDashboardData } from "@/lib/dashboard-context";
import { ExternalLink } from "lucide-react";
import { useMemo } from "react";

export const Route = createFileRoute("/sources")({
  head: () => ({
    meta: [
      { title: "Sources — MorningPulse AI" },
      { name: "description", content: "Monitored sources and sync status." },
    ],
  }),
  component: SourcesRoute,
});

function SourcesRoute() {
  return (
    <DashboardLayout>
      <SourcesContent />
    </DashboardLayout>
  );
}

function SourcesContent() {
  const { digest, isLoading, error } = useDashboardData();

  // Extract and aggregate sources from digest
  const sources = useMemo(() => {
    if (!digest) return [];

    const sourceMap = new Map<string, { name: string; count: number; urls: string[] }>();

    // Helper to add source
    const addSource = (sourceName: string, url?: string) => {
      if (!sourceName || sourceName === "N/A" || sourceName === "unknown") return;
      
      const normalizedName = sourceName.trim();
      const existing = sourceMap.get(normalizedName);
      
      if (existing) {
        existing.count++;
        if (url && url !== "#" && !existing.urls.includes(url)) {
          existing.urls.push(url);
        }
      } else {
        sourceMap.set(normalizedName, {
          name: normalizedName,
          count: 1,
          urls: url && url !== "#" ? [url] : [],
        });
      }
    };

    // Extract from competitor updates
    digest.competitor_updates?.forEach((update: any) => {
      update.sources?.forEach((source: any) => {
        addSource(source.source_name, source.url);
      });
    });

    // Extract from user pain points
    digest.user_pain_points?.forEach((point: any) => {
      point.sources?.forEach((source: any) => {
        addSource(source.source_name, source.url);
      });
    });

    // Extract from emerging trends
    digest.emerging_tech_trends?.forEach((trend: any) => {
      trend.sources?.forEach((source: any) => {
        addSource(source.source_name, source.url);
      });
    });

    // Extract from customer risk alerts
    digest.customer_risk_alerts?.forEach((alert: any) => {
      alert.sources?.forEach((source: any) => {
        addSource(source.source_name, source.url);
      });
    });

    // Extract from battle cards
    digest.battle_cards?.forEach((card: any) => {
      card.sources?.forEach((source: any) => {
        addSource(source.source_name, source.url);
      });
    });

    // Convert to array and sort by count (descending)
    return Array.from(sourceMap.values()).sort((a, b) => b.count - a.count);
  }, [digest]);

  // Calculate stats
  const totalSources = sources.length;
  const totalArticles = sources.reduce((sum, s) => sum + s.count, 0);
  const activeSources = sources.filter((s) => s.count > 0).length;

  return (
    <div className="mx-auto max-w-6xl space-y-6">
        <SectionHeader
          title="Sources"
          description="Monitored feeds and integrations from today's digest."
        />

        {/* Stats Cards */}
        <div className="grid gap-4 sm:grid-cols-3">
          <Card className="border-border p-4 shadow-none">
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Total Sources
            </p>
            <p className="mt-1 text-2xl font-semibold text-foreground">{totalSources}</p>
          </Card>
          <Card className="border-border p-4 shadow-none">
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Active Sources
            </p>
            <p className="mt-1 text-2xl font-semibold text-foreground">{activeSources}</p>
          </Card>
          <Card className="border-border p-4 shadow-none">
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Total Articles
            </p>
            <p className="mt-1 text-2xl font-semibold text-foreground">{totalArticles}</p>
          </Card>
        </div>

        {/* Loading State */}
        {isLoading && (
          <Card className="border-border p-6 shadow-none">
            <p className="text-sm text-muted-foreground">Loading sources...</p>
          </Card>
        )}

        {/* Error State */}
        {!isLoading && error && (
          <Card className="border-border p-6 shadow-none">
            <p className="text-sm text-destructive">{error}</p>
          </Card>
        )}

        {/* Empty State */}
        {!isLoading && !error && sources.length === 0 && (
          <Card className="border-dashed border-border p-8 text-center shadow-none">
            <p className="text-sm text-muted-foreground">
              No sources available yet. Run the pipeline to generate digest.
            </p>
          </Card>
        )}

        {/* Sources List */}
        {!isLoading && !error && sources.length > 0 && (
          <Card className="border-border p-0 shadow-none">
            <ul className="divide-y divide-border">
              {sources.map((source) => (
                <li
                  key={source.name}
                  className="flex items-center justify-between gap-4 px-5 py-4 transition-colors hover:bg-muted/50"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-foreground">{source.name}</p>
                      <Badge variant="secondary" className="text-xs">
                        {source.count} {source.count === 1 ? "article" : "articles"}
                      </Badge>
                    </div>
                    {source.urls.length > 0 && (
                      <div className="mt-1 flex flex-wrap gap-2">
                        {source.urls.slice(0, 3).map((url, idx) => (
                          <a
                            key={idx}
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-xs text-primary underline hover:text-primary/80"
                          >
                            View article
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        ))}
                        {source.urls.length > 3 && (
                          <span className="text-xs text-muted-foreground">
                            +{source.urls.length - 3} more
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                  <Badge
                    variant="outline"
                    className="shrink-0 border-green-200 bg-green-50 text-green-700 dark:border-green-800 dark:bg-green-950/20 dark:text-green-400"
                  >
                    Active
                  </Badge>
                </li>
              ))}
            </ul>
          </Card>
        )}

        {/* Source Types Breakdown */}
        {!isLoading && !error && sources.length > 0 && (
          <Card className="border-border p-6 shadow-none">
            <h3 className="text-sm font-semibold text-foreground">Source Distribution</h3>
            <div className="mt-4 space-y-2">
              {sources.slice(0, 10).map((source) => (
                <div key={source.name} className="flex items-center gap-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-2">
                      <p className="truncate text-xs text-muted-foreground">{source.name}</p>
                      <p className="shrink-0 text-xs font-medium text-foreground">
                        {source.count}
                      </p>
                    </div>
                    <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full bg-primary"
                        style={{
                          width: `${(source.count / totalArticles) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
  );
}
