import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, CheckCircle2, ExternalLink } from "lucide-react";

interface CustomerRiskAlert {
  type: string;
  company: string;
  event: string;
  risk_level: "High" | "Medium";
  risk_score: number;
  why_it_matters: string;
  recommended_action: string;
  sources?: Array<{ source_name: string; url?: string }>;
}

interface CustomerRiskAlertProps {
  alerts: CustomerRiskAlert[];
}

export function CustomerRiskAlert({ alerts }: CustomerRiskAlertProps) {
  // No alerts - show green status
  if (!alerts || alerts.length === 0) {
    return (
      <Card className="border-green-200 bg-green-50 p-6 shadow-none dark:border-green-800 dark:bg-green-950/20">
        <div className="flex items-center gap-3">
          <CheckCircle2 className="h-6 w-6 text-green-600 dark:text-green-400" />
          <div>
            <h3 className="text-sm font-semibold text-green-900 dark:text-green-100">
              No Immediate Customer Risk Detected
            </h3>
            <p className="mt-1 text-xs text-green-700 dark:text-green-300">
              All competitor activity is within normal parameters
            </p>
          </div>
        </div>
      </Card>
    );
  }

  // Get highest risk alert
  const topAlert = alerts[0];
  const isHighRisk = topAlert.risk_level === "High";

  return (
    <div className="space-y-3">
      {/* Top Priority Alert */}
      <Card
        className={`border-2 p-6 shadow-md ${
          isHighRisk
            ? "border-red-500 bg-red-50 dark:border-red-700 dark:bg-red-950/20"
            : "border-amber-500 bg-amber-50 dark:border-amber-700 dark:bg-amber-950/20"
        }`}
      >
        <div className="flex items-start gap-4">
          <AlertTriangle
            className={`h-7 w-7 shrink-0 ${
              isHighRisk
                ? "text-red-600 dark:text-red-400"
                : "text-amber-600 dark:text-amber-400"
            }`}
          />
          <div className="min-w-0 flex-1 space-y-3">
            <div>
              <div className="flex items-center gap-2">
                <h3
                  className={`text-sm font-bold uppercase tracking-wider ${
                    isHighRisk
                      ? "text-red-900 dark:text-red-100"
                      : "text-amber-900 dark:text-amber-100"
                  }`}
                >
                  🔴 CUSTOMER RISK ALERT
                </h3>
                <Badge
                  variant={isHighRisk ? "destructive" : "default"}
                  className="text-xs font-semibold"
                >
                  {topAlert.risk_level} Risk
                </Badge>
              </div>
              <p
                className={`mt-2 text-base font-semibold ${
                  isHighRisk
                    ? "text-red-900 dark:text-red-100"
                    : "text-amber-900 dark:text-amber-100"
                }`}
              >
                {topAlert.company} — {topAlert.event}
              </p>
            </div>

            <div className="space-y-2">
              <div>
                <p
                  className={`text-xs font-medium uppercase tracking-wider ${
                    isHighRisk
                      ? "text-red-700 dark:text-red-300"
                      : "text-amber-700 dark:text-amber-300"
                  }`}
                >
                  Why It Matters
                </p>
                <p
                  className={`mt-1 text-sm ${
                    isHighRisk
                      ? "text-red-800 dark:text-red-200"
                      : "text-amber-800 dark:text-amber-200"
                  }`}
                >
                  {topAlert.why_it_matters}
                </p>
              </div>

              <div>
                <p
                  className={`text-xs font-medium uppercase tracking-wider ${
                    isHighRisk
                      ? "text-red-700 dark:text-red-300"
                      : "text-amber-700 dark:text-amber-300"
                  }`}
                >
                  Recommended Action
                </p>
                <p
                  className={`mt-1 text-sm font-semibold ${
                    isHighRisk
                      ? "text-red-900 dark:text-red-100"
                      : "text-amber-900 dark:text-amber-100"
                  }`}
                >
                  {topAlert.recommended_action}
                </p>
              </div>

              {topAlert.sources && topAlert.sources.length > 0 && (
                <div className="flex flex-wrap gap-2 pt-1">
                  {topAlert.sources.map((source, idx) =>
                    source.url && source.url !== "#" ? (
                      <a
                        key={idx}
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`inline-flex items-center gap-1 text-xs underline ${
                          isHighRisk
                            ? "text-red-700 hover:text-red-900 dark:text-red-300 dark:hover:text-red-100"
                            : "text-amber-700 hover:text-amber-900 dark:text-amber-300 dark:hover:text-amber-100"
                        }`}
                      >
                        {source.source_name}
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    ) : (
                      <span
                        key={idx}
                        className={`text-xs ${
                          isHighRisk
                            ? "text-red-600 dark:text-red-400"
                            : "text-amber-600 dark:text-amber-400"
                        }`}
                      >
                        {source.source_name}
                      </span>
                    )
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </Card>

      {/* Additional Alerts (if any) */}
      {alerts.length > 1 && (
        <div className="space-y-2">
          <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
            Additional Risks ({alerts.length - 1})
          </p>
          <div className="grid gap-2 sm:grid-cols-2">
            {alerts.slice(1).map((alert, idx) => (
              <Card
                key={idx}
                className="border-border bg-muted/50 p-4 shadow-none transition-colors hover:bg-muted"
              >
                <div className="flex items-start gap-2">
                  <Badge
                    variant={alert.risk_level === "High" ? "destructive" : "default"}
                    className="shrink-0 text-[10px]"
                  >
                    {alert.risk_level}
                  </Badge>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-semibold text-foreground">
                      {alert.company}
                    </p>
                    <p className="mt-0.5 text-xs text-muted-foreground">
                      {alert.event}
                    </p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
