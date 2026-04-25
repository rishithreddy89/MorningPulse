import { Link, useLocation } from "@tanstack/react-router";
import { LayoutDashboard, TrendingUp, Database, Settings, RefreshCw, Linkedin, Activity } from "lucide-react";
import { useMemo, type ReactNode } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { DashboardDataProvider, useDashboardData } from "@/lib/dashboard-context";
import { cn } from "@/lib/utils";

const nav = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/trends", label: "Trends", icon: TrendingUp },
  { to: "/sources", label: "Sources", icon: Database },
  { to: "/linkedin", label: "LinkedIn Intel", icon: Linkedin },
  { to: "/settings", label: "Settings", icon: Settings },
] as const;

export function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <DashboardDataProvider>
      <DashboardLayoutShell>{children}</DashboardLayoutShell>
    </DashboardDataProvider>
  );
}

function DashboardLayoutShell({ children }: { children: ReactNode }) {
  const { pathname } = useLocation();
  const { dates, digest, selectedDate, isRefreshing, isLoading, selectDate, refreshDigest } =
    useDashboardData();

  const dateOptions = useMemo(() => {
    if (digest?.date && !dates.includes(digest.date)) {
      return [digest.date, ...dates];
    }
    return dates;
  }, [dates, digest?.date]);

  const handleRefresh = async () => {
    const loadingToast = toast.loading("Refreshing data...");
    const ok = await refreshDigest();

    if (ok) {
      toast.success("Digest refreshed", { id: loadingToast });
      return;
    }

    toast.error("Backend not reachable. Start server.", { id: loadingToast });
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-border bg-card px-6">
        <div className="flex items-center gap-2">
          <div className="h-6 w-6 rounded-md bg-primary" aria-hidden />
          <span className="text-sm font-semibold tracking-tight">MorningPulse AI</span>
        </div>
        <div className="flex items-center gap-2">
          
          <Select
            value={selectedDate ?? undefined}
            onValueChange={(value) => {
              void selectDate(value);
            }}
            disabled={isLoading || dateOptions.length === 0}
          >
            <SelectTrigger className="h-9 w-[150px] text-sm">
              <SelectValue placeholder={dateOptions.length > 0 ? "Select date" : "No dates"} />
            </SelectTrigger>
            <SelectContent>
              {dateOptions.map((date) => (
                <SelectItem key={date} value={date}>
                  {date}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="h-9 gap-2"
          >
            <RefreshCw className={cn("h-4 w-4", isRefreshing && "animate-spin")} />
            Refresh
          </Button>
        </div>
      </header>

      <div className="flex">
        <aside className="sticky top-14 hidden h-[calc(100vh-3.5rem)] w-56 shrink-0 border-r border-border bg-card md:block">
          <nav className="flex flex-col gap-1 p-3">
            {nav.map((item) => {
              const active = pathname === item.to;
              const Icon = item.icon;
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={cn(
                    "flex items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    active
                      ? "bg-accent text-accent-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground",
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </aside>

        <main className="min-w-0 flex-1 px-4 py-6 md:px-8 md:py-8">{children}</main>
      </div>
    </div>
  );
}
