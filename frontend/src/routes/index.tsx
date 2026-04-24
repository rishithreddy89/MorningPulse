import { createFileRoute } from "@tanstack/react-router";
import { DashboardLayout } from "@/components/DashboardLayout";
import { DashboardPage } from "@/components/dashboard/DashboardPage";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Dashboard — MorningPulse AI" },
      {
        name: "description",
        content:
          "Daily intelligence brief: high priority alerts, emerging trends, pain points, and competitor updates.",
      },
      { property: "og:title", content: "Dashboard — MorningPulse AI" },
      {
        property: "og:description",
        content: "Daily intelligence dashboard for product and strategy teams.",
      },
    ],
  }),
  component: Index,
});

function Index() {
  return (
    <DashboardLayout>
      <DashboardPage />
    </DashboardLayout>
  );
}
