import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card } from "@/components/ui/card";
import { SectionHeader } from "@/components/dashboard/Primitives";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Download, Mail } from "lucide-react";
import { useDashboardData } from "@/lib/dashboard-context";
import { API_BASE } from "@/lib/api";

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
      <SettingsContent />
    </DashboardLayout>
  );
}

function SettingsContent() {
  const { selectedDate } = useDashboardData();
  const [orgName, setOrgName] = useState("Acme Education");
  const [email, setEmail] = useState("brief@acme.edu");
  const [deliveryTime, setDeliveryTime] = useState("08:00");
  const [emailBrief, setEmailBrief] = useState(true);
  const [includeCompetitors, setIncludeCompetitors] = useState(true);
  const [includeLowPriority, setIncludeLowPriority] = useState(false);
  const [nextDelivery, setNextDelivery] = useState<string | null>(null);

  const [downloadLoading, setDownloadLoading] = useState(false);
  const [emailLoading, setEmailLoading] = useState(false);
  const [saveLoading, setSaveLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  // Get user's timezone
  const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

  // Calculate next delivery time
  const calculateNextDelivery = (time: string) => {
    const [hours, mins] = time.split(":").map(Number);
    const next = new Date();
    next.setHours(hours, mins, 0, 0);
    if (next <= new Date()) {
      next.setDate(next.getDate() + 1);
    }
    return next.toLocaleString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Load saved settings on mount
  useEffect(() => {
    const loadSettings = async () => {
      try {
        const res = await fetch(`${API_BASE}/settings`);
        if (res.ok) {
          const settings = await res.json();
          setOrgName(settings.organization || "MorningPulse AI");
          setEmail(settings.email || "");
          setDeliveryTime(settings.delivery_time || "08:00");
          setEmailBrief(settings.email_enabled ?? true);
          setIncludeCompetitors(settings.include_competitors ?? true);
          setIncludeLowPriority(settings.include_low_priority ?? false);
          setNextDelivery(calculateNextDelivery(settings.delivery_time || "08:00"));
        }
      } catch (err) {
        console.error("Failed to load settings:", err);
      }
    };
    loadSettings();
  }, []);

  // Update next delivery when time changes
  useEffect(() => {
    setNextDelivery(calculateNextDelivery(deliveryTime));
  }, [deliveryTime]);

  const handleSaveSettings = async () => {
    setSaveLoading(true);

    try {
      const settings = {
        organization: orgName,
        email,
        delivery_time: deliveryTime,
        email_enabled: emailBrief,
        include_competitors: includeCompetitors,
        include_low_priority: includeLowPriority,
      };

      const res = await fetch(`${API_BASE}/settings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(settings),
      });

      const data = await res.json();

      if (data.success) {
        showStatus("success", data.message || "Settings saved successfully");
        setNextDelivery(calculateNextDelivery(deliveryTime));
      } else {
        showStatus("error", data.error || "Failed to save settings");
      }
    } catch (err) {
      showStatus("error", "Network error. Is the backend running?");
    } finally {
      setSaveLoading(false);
    }
  };

  const showStatus = (type: "success" | "error", text: string) => {
    setStatusMessage({ type, text });
    setTimeout(() => setStatusMessage(null), 5000);
  };

  const handleDownloadPDF = () => {
    setDownloadLoading(true);
    const date = selectedDate || new Date().toISOString().split("T")[0];

    // Trigger download via anchor
    const link = document.createElement("a");
    link.href = `${API_BASE}/export/pdf?date=${date}`;
    link.download = `morningpulse-${date}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setTimeout(() => {
      setDownloadLoading(false);
      showStatus("success", "PDF download started");
    }, 1000);
  };

  const handleSendEmail = async () => {
    if (!email) {
      showStatus("error", "Please enter a notification email first");
      return;
    }

    setEmailLoading(true);

    try {
      const date = selectedDate || new Date().toISOString().split("T")[0];
      const res = await fetch(`${API_BASE}/export/email`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          date,
          settings: { organization: orgName },
        }),
      });

      const data = await res.json();

      if (data.success) {
        showStatus("success", `Report sent to ${email} successfully!`);
      } else {
        showStatus("error", data.error || "Failed to send. Check SMTP settings.");
      }
    } catch (err) {
      showStatus("error", "Network error. Is the backend running?");
    } finally {
      setEmailLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <SectionHeader title="Settings" description="Manage your workspace preferences." />

      <Card className="border-border p-6 shadow-none">
        <h3 className="text-sm font-semibold">Workspace</h3>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <div className="space-y-1.5">
            <Label htmlFor="org">Organization</Label>
            <Input
              id="org"
              value={orgName}
              onChange={(e) => setOrgName(e.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="email">Notification email</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
        </div>
      </Card>

      <Card className="border-border p-6 shadow-none">
        <h3 className="text-sm font-semibold">Daily brief</h3>
        <div className="mt-4 space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-4">
            <p className="text-sm">Email me the daily brief</p>
            <Switch checked={emailBrief} onCheckedChange={setEmailBrief} />
          </div>
          <div className="flex items-center justify-between border-b border-border pb-4">
            <p className="text-sm">Include competitor updates</p>
            <Switch checked={includeCompetitors} onCheckedChange={setIncludeCompetitors} />
          </div>
          <div className="flex items-center justify-between border-b border-border pb-4">
            <p className="text-sm">Include low priority alerts</p>
            <Switch checked={includeLowPriority} onCheckedChange={setIncludeLowPriority} />
          </div>
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-sm font-medium">Daily brief delivery time</p>
              <p className="text-xs text-muted-foreground">
                CEO receives the PDF report at this time every day ({userTimezone})
              </p>
            </div>
            <div className="flex flex-col items-end gap-2">
              <Input
                type="time"
                value={deliveryTime}
                onChange={(e) => setDeliveryTime(e.target.value)}
                className="w-32"
              />
              {nextDelivery && (
                <p className="text-xs text-muted-foreground">
                  Next: {nextDelivery}
                </p>
              )}
            </div>
          </div>
        </div>
      </Card>

      <Card className="border-border p-6 shadow-none">
        <h3 className="text-sm font-semibold">Report Export</h3>
        <div className="mt-4 space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-4">
            <div>
              <p className="text-sm font-medium">Download today's digest as PDF</p>
              <p className="text-xs text-muted-foreground">
                Generates a branded A4 report with all insights
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleDownloadPDF}
              disabled={downloadLoading}
              className="gap-2"
            >
              <Download className="h-4 w-4" />
              {downloadLoading ? "Generating..." : "Download PDF"}
            </Button>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Email report now</p>
              <p className="text-xs text-muted-foreground">
                Sends PDF to the notification email above
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleSendEmail}
              disabled={emailLoading}
              className="gap-2"
            >
              <Mail className="h-4 w-4" />
              {emailLoading ? "Sending..." : "Send Now"}
            </Button>
          </div>
        </div>
      </Card>

      {statusMessage && (
        <Alert
          variant={statusMessage.type === "error" ? "destructive" : "default"}
          className="border-border"
        >
          <AlertDescription>{statusMessage.text}</AlertDescription>
        </Alert>
      )}

      <div className="flex justify-end">
        <Button onClick={handleSaveSettings} disabled={saveLoading}>
          {saveLoading ? "Saving..." : "Save changes"}
        </Button>
      </div>
    </div>
  );
}
