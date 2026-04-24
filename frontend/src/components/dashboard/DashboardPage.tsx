import { Card } from "@/components/ui/card";
import { SectionHeader } from "@/components/dashboard/Primitives";
import { useDashboardData } from "@/lib/dashboard-context";

export function DashboardPage() {
  const { digest, isLoading, error } = useDashboardData();

  console.log("DIGEST:", digest);

  const trends = digest?.emerging_tech_trends ?? [];
  console.log("Emerging Trends:", trends);
  const painPoints = digest?.user_pain_points ?? [];
  const competitors = digest?.competitor_updates ?? [];

  const hasDigestData = !!digest && (trends.length > 0 || painPoints.length > 0 || competitors.length > 0);
  const isEmpty = !isLoading && !error && !hasDigestData;

  const renderTrends = () => (
    <section>
      <SectionHeader
        title="Emerging Trends"
        description="Signals aggregated across forums, RFPs, and industry coverage."
      />
      {trends.length === 0 ? (
        <Card className="border-dashed border-border p-8 text-center shadow-none">
          <p className="text-sm text-muted-foreground">No emerging trends available.</p>
        </Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {trends.map((trend, index) => (
            <Card
              key={`${trend.trend}-${index}`}
              className="trend-card border-border p-5 shadow-none transition-shadow hover:shadow-[var(--shadow-card)]"
            >
              <h3 className="text-sm font-semibold text-foreground">{trend.trend}</h3>
              <p className="mt-1.5 text-sm text-muted-foreground">
                {trend.explanation && trend.explanation.trim() !== ""
                  ? trend.explanation
                  : `${trend.trend} is an emerging area in EdTech. Click the sources below to learn more.`}
              </p>
              {trend.sources && trend.sources.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {trend.sources.map((source, idx) => (
                    source.url && source.url !== "#" && source.url !== "N/A" ? (
                      <a
                        key={idx}
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-primary underline hover:text-primary/80"
                      >
                        {source.source_name}
                      </a>
                    ) : (
                      <span key={idx} className="text-xs text-muted-foreground">
                        {source.source_name}
                      </span>
                    )
                  ))}
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </section>
  );

  const renderPainPoints = () => (
    <section>
      <SectionHeader
        title="User Pain Points"
        description="Recurring frustrations from customers and prospects."
      />
      {painPoints.length === 0 ? (
        <Card className="border-dashed border-border p-8 text-center shadow-none">
          <p className="text-sm text-muted-foreground">No user pain points available.</p>
        </Card>
      ) : (
        <Card className="border-border p-0 shadow-none">
          <ul className="divide-y divide-border">
            {painPoints.map((point, index) => (
              <li
                key={`${point.issue}-${index}`}
                className="flex items-start gap-4 px-5 py-4 transition-colors hover:bg-muted/50"
              >
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-foreground">{point.issue}</p>
                  <p className="mt-1 text-xs text-muted-foreground">{point.context}</p>
                  {point.sources && point.sources.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {point.sources.map((source, idx) => (
                        source.url && source.url !== "#" && source.url !== "N/A" ? (
                          <a
                            key={idx}
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-primary underline hover:text-primary/80"
                          >
                            {source.source_name}
                          </a>
                        ) : (
                          <span key={idx} className="text-xs text-muted-foreground">
                            {source.source_name}
                          </span>
                        )
                      ))}
                    </div>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </Card>
      )}
    </section>
  );

  const renderCompetitors = () => (
    <section>
      <SectionHeader
        title="Competitor Updates"
        description="Recent moves from companies in your tracked set."
      />
      {competitors.length === 0 ? (
        <Card className="border-dashed border-border p-8 text-center shadow-none">
          <p className="text-sm text-muted-foreground">No competitor updates available.</p>
        </Card>
      ) : (
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {competitors.map((competitor, index) => (
            <Card
              key={`${competitor.title}-${index}`}
              className="flex flex-col border-border p-5 shadow-none transition-shadow hover:shadow-[var(--shadow-elevated)]"
            >
              <h3 className="text-sm font-semibold text-foreground">{competitor.title}</h3>
              <p className="mt-1.5 flex-1 text-sm text-muted-foreground">{competitor.description}</p>
              {competitor.sources && competitor.sources.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {competitor.sources.map((source, idx) => (
                    source.url && source.url !== "#" && source.url !== "N/A" ? (
                      <a
                        key={idx}
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-primary underline hover:text-primary/80"
                      >
                        {source.source_name}
                      </a>
                    ) : (
                      <span key={idx} className="text-xs text-muted-foreground">
                        {source.source_name}
                      </span>
                    )
                  ))}
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </section>
  );

  const renderDashboard = () => (
    <>
      {renderTrends()}
      {renderPainPoints()}
      {renderCompetitors()}
    </>
  );

  return (
    <div className="mx-auto max-w-6xl space-y-10">
      <header>
        <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
          Daily brief
        </p>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight text-foreground">Dashboard</h1>
      </header>

      {isLoading && (
        <Card className="border-border p-6 shadow-none">
          <p className="text-sm text-muted-foreground">Loading dashboard...</p>
        </Card>
      )}

      {!isLoading && error && (
        <Card className="border-border p-6 shadow-none">
          <p className="text-sm text-destructive">{error}</p>
        </Card>
      )}

      {isEmpty && (
        <Card className="border-border p-6 shadow-none">
          <p className="text-sm text-muted-foreground">No data yet. Click refresh.</p>
        </Card>
      )}

      {!isLoading && !error && hasDigestData && renderDashboard()}
    </div>
  );
}
