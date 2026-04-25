import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { SectionHeader } from "@/components/dashboard/Primitives";
import { PainPointCard } from "@/components/dashboard/PainPointCard";
import { CustomerRiskAlert } from "@/components/dashboard/CustomerRiskAlert";
import { FloatingChat } from "@/components/FloatingChat";
import { VoiceDigest } from "@/components/VoiceDigest";
import { useDashboardData } from "@/lib/dashboard-context";
import { useEffect, useState } from "react";
import { fetchBattleCards, type BattleCard } from "@/lib/api";

export function DashboardPage() {
  const { digest, isLoading, error } = useDashboardData();
  const [battleCards, setBattleCards] = useState<BattleCard[]>([]);
  const [battleCardsLoading, setBattleCardsLoading] = useState(false);

  useEffect(() => {
    const loadBattleCards = async () => {
      setBattleCardsLoading(true);
      const data = await fetchBattleCards();
      if (data) {
        setBattleCards(data.battle_cards);
      }
      setBattleCardsLoading(false);
    };
    void loadBattleCards();
  }, [digest]);

  console.log("DIGEST:", digest);

  const trends = digest?.emerging_tech_trends ?? [];
  console.log("Emerging Trends:", trends);
  const painPoints = digest?.user_pain_points ?? [];
  const competitors = digest?.competitor_updates ?? [];
  const customerRiskAlerts = digest?.customer_risk_alerts ?? [];

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
              <PainPointCard
                key={`${point.issue}-${index}`}
                issue={point.issue}
                context={point.context}
                sources={point.sources}
                index={index}
              />
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

  const getThreatBadgeVariant = (level: string) => {
    if (level === "high") return "destructive";
    if (level === "medium") return "default";
    return "secondary";
  };

  const getResponseBadgeVariant = (response: string) => {
    if (response === "immediate") return "destructive";
    if (response === "monitor") return "default";
    return "secondary";
  };

  const renderBattleCards = () => (
    <section>
      <SectionHeader
        title="Competitive Battle Cards"
        description="Auto-generated intelligence for every competitor detected today"
      />
      {battleCardsLoading ? (
        <Card className="border-border p-6 shadow-none">
          <p className="text-sm text-muted-foreground">Loading battle cards...</p>
        </Card>
      ) : battleCards.length === 0 ? (
        <Card className="border-dashed border-border p-8 text-center shadow-none">
          <p className="text-sm text-muted-foreground">
            No battle cards available. Trigger a pipeline run to generate them.
          </p>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {battleCards.map((card, index) => (
            <Card
              key={`${card.competitor_name}-${index}`}
              className="flex flex-col border-border p-5 shadow-none transition-shadow hover:shadow-[var(--shadow-elevated)]"
            >
              <div className="mb-4 flex items-center justify-between border-b border-border pb-3">
                <h3 className="text-sm font-semibold text-foreground">{card.competitor_name}</h3>
                <Badge variant={getThreatBadgeVariant(card.threat_level)} className="text-xs">
                  {card.threat_level} threat
                </Badge>
              </div>

              <div className="space-y-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Their Strength
                  </p>
                  <p className="mt-1 text-sm text-foreground">{card.their_strength}</p>
                </div>

                <div className="rounded-md border-l-4 border-red-500 bg-red-50 p-3 dark:bg-red-950/20">
                  <p className="text-xs font-semibold uppercase tracking-wider text-red-700 dark:text-red-400">
                    Their Weakness
                  </p>
                  <p className="mt-1 text-sm text-red-900 dark:text-red-300">{card.their_weakness}</p>
                </div>

                <div className="rounded-md border-l-4 border-blue-500 bg-blue-50 p-3 dark:bg-blue-950/20">
                  <p className="text-xs font-semibold uppercase tracking-wider text-blue-700 dark:text-blue-400">
                    Our Advantage
                  </p>
                  <p className="mt-1 text-sm text-blue-900 dark:text-blue-300">
                    {card.campus_cortex_advantage}
                  </p>
                </div>

                <div className="rounded-md bg-muted p-3">
                  <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Sales Talking Point
                  </p>
                  <p className="mt-1 text-sm italic text-foreground">"{card.sales_talking_point}"</p>
                </div>

                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Pricing Signal
                  </p>
                  <p className="mt-1 text-sm text-foreground">{card.pricing_signal}</p>
                </div>

                <div className="flex items-center justify-between pt-2">
                  <Badge variant={getResponseBadgeVariant(card.recommended_response)} className="text-xs">
                    {card.recommended_response.toUpperCase()}
                  </Badge>
                </div>

                <div>
                  <p className="text-xs text-muted-foreground">{card.response_action}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </section>
  );

  const renderDashboard = () => (
    <>
      <VoiceDigest digest={digest} />
      {customerRiskAlerts.length > 0 && (
        <section>
          <SectionHeader
            title="Customer Risk Alert"
            description="High-priority competitor actions that may impact customer retention"
          />
          <CustomerRiskAlert alerts={customerRiskAlerts} />
        </section>
      )}
      {renderTrends()}
      {renderPainPoints()}
      {renderCompetitors()}
      {renderBattleCards()}
    </>
  );

  return (
    <>
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

      {/* Floating Chat Widget */}
      <FloatingChat date={digest?.date} />
    </>
  );
}
