import { cn } from "@/lib/utils";
import type { Urgency } from "@/lib/dashboard-data";

export function UrgencyBadge({ urgency }: { urgency: Urgency }) {
  const styles: Record<Urgency, string> = {
    high: "bg-destructive text-destructive-foreground",
    medium: "bg-warning/15 text-warning border border-warning/30",
    low: "bg-muted text-muted-foreground border border-border",
  };
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium capitalize",
        styles[urgency],
      )}
    >
      {urgency}
    </span>
  );
}

export function ImpactBadge({ score }: { score: number }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-md border border-border bg-muted px-2 py-0.5 text-xs font-medium tabular-nums text-foreground">
      <span className="text-muted-foreground">Impact</span>
      {score}
    </span>
  );
}

export function SectionHeader({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="mb-4 flex items-end justify-between gap-4">
      <div>
        <h2 className="text-base font-semibold tracking-tight text-foreground">{title}</h2>
        {description && (
          <p className="mt-0.5 text-sm text-muted-foreground">{description}</p>
        )}
      </div>
      {action}
    </div>
  );
}
