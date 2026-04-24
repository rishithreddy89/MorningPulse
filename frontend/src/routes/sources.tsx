import { createFileRoute } from "@tanstack/react-router";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card } from "@/components/ui/card";
import { SectionHeader } from "@/components/dashboard/Primitives";

const sources = [
  { name: "EdSurge", status: "Active", lastSync: "12 min ago" },
  { name: "K-12 Dive", status: "Active", lastSync: "18 min ago" },
  { name: "EdWeek", status: "Active", lastSync: "32 min ago" },
  { name: "District Administration", status: "Active", lastSync: "45 min ago" },
  { name: "r/k12sysadmin", status: "Active", lastSync: "1 hr ago" },
  { name: "ED.gov", status: "Active", lastSync: "2 hr ago" },
];

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
      <div className="mx-auto max-w-6xl">
        <SectionHeader title="Sources" description="Monitored feeds and integrations." />
        <Card className="border-border p-0 shadow-none">
          <ul className="divide-y divide-border">
            {sources.map((s) => (
              <li
                key={s.name}
                className="flex items-center justify-between px-5 py-4 hover:bg-muted/50"
              >
                <div>
                  <p className="text-sm font-medium text-foreground">{s.name}</p>
                  <p className="mt-0.5 text-xs text-muted-foreground">
                    Last sync: {s.lastSync}
                  </p>
                </div>
                <span className="rounded-full border border-success/30 bg-success/10 px-2 py-0.5 text-xs font-medium text-success">
                  {s.status}
                </span>
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </DashboardLayout>
  );
}
