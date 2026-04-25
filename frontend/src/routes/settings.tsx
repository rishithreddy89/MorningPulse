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
  const [emailBrief, setEmailBrief] = useState(true);
  const [includeCompetitors, setIncludeCompetitors] = useState(true);
  const [includeLowPriority, setIncludeLowPriority] = useState(false);

  const [downloadLoading, setDownloadLoading] = useState(false);
  const [emailLoading, setEmailLoading] = useState(false);
  const [saveLoading, setSaveLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  // Load saved settings on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem("morningpulse_settings");
      if (saved) {
        const settings = JSON.parse(saved);
        setOrgName(settings.organization || "Acme Education");
        setEmail(settings.email || "brief@acme.edu");
        setEmailBrief(settings.emailBrief ?? true);
        setIncludeCompetitors(settings.includeCompetitors ?? true);
        setIncludeLowPriority(settings.includeLowPriority ?? false);
      }
    } catch (err) {
      console.error("Failed to load settings:", err);
    }
  }, []);

  const handleSaveSettings = async () => {
    setSaveLoading(true);

    try {
      // Save settings to localStorage for now
      // In production, this would be an API call to save to database
      const settings = {
        organization: orgName,
        email,
        emailBrief,
        includeCompetitors,
        includeLowPriority,
      };

      localStorage.setItem("morningpulse_settings", JSON.stringify(settings));

      // Simulate API call delay
      await new Promise((resolve) => setTimeout(resolve, 500));

      showStatus("success", "Settings saved successfully");
    } catch (err) {
      showStatus("error", "Failed to save settings");
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
          <div className="flex items-center justify-between">
            <p className="text-sm">Include low priority alerts</p>
            <Switch checked={includeLowPriority} onCheckedChange={setIncludeLowPriority} />
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
