import { createFileRoute } from "@tanstack/react-router";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card } from "@/components/ui/card";
import { SectionHeader } from "@/components/dashboard/Primitives";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/settings")({
  head: () => ({
    meta: [
      { title: "Settings — MorningPulse AI" },
      { name: "description", content: "Account and notification preferences." },
    ],
  }),
  component: SettingsRoute,
});

function SettingsRoute() {
  return (
    <DashboardLayout>
      <div className="mx-auto max-w-3xl space-y-8">
        <SectionHeader title="Settings" description="Manage your workspace preferences." />

        <Card className="border-border p-6 shadow-none">
          <h3 className="text-sm font-semibold">Workspace</h3>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label htmlFor="org">Organization</Label>
              <Input id="org" defaultValue="Acme Education" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="email">Notification email</Label>
              <Input id="email" type="email" defaultValue="brief@acme.edu" />
            </div>
          </div>
        </Card>

        <Card className="border-border p-6 shadow-none">
          <h3 className="text-sm font-semibold">Daily brief</h3>
          <div className="mt-4 space-y-4">
            {[
              { label: "Email me the daily brief", defaultChecked: true },
              { label: "Include competitor updates", defaultChecked: true },
              { label: "Include low priority alerts", defaultChecked: false },
            ].map((row) => (
              <div
                key={row.label}
                className="flex items-center justify-between border-b border-border pb-4 last:border-0 last:pb-0"
              >
                <p className="text-sm">{row.label}</p>
                <Switch defaultChecked={row.defaultChecked} />
              </div>
            ))}
          </div>
        </Card>

        <div className="flex justify-end">
          <Button>Save changes</Button>
        </div>
      </div>
    </DashboardLayout>
  );
}
