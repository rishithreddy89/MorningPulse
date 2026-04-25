import { useEffect, useRef, useState } from "react";
import { X, Activity, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { API_BASE } from "@/lib/api";

interface WarRoomEvent {
  type: string;
  ts: string;
  message?: string;
  source?: string;
  title?: string;
  category?: string;
  competitor?: string;
  count?: number;
  counts?: Record<string, number>;
  text?: string;
  score?: number;
  total_signals?: number;
}

interface FeedItem {
  type: string;
  text: string;
  ts: string;
  id: string;
}

interface SourceStatus {
  status: "waiting" | "running" | "complete";
  count: number;
}

export function WarRoom({ onClose }: { onClose: () => void }) {
  const [isConnected, setIsConnected] = useState(false);
  const [feed, setFeed] = useState<FeedItem[]>([]);
  const [signalCount, setSignalCount] = useState(0);
  const [alertCount, setAlertCount] = useState(0);
  const [pulseScore, setPulseScore] = useState(0);
  const [currentTime, setCurrentTime] = useState("");
  const [categoryBreakdown, setCategoryBreakdown] = useState({
    competitor: 0,
    trend: 0,
    pain_point: 0,
    signal: 0,
  });
  const [sourceStatus, setSourceStatus] = useState<Record<string, SourceStatus>>({
    hackernews: { status: "waiting", count: 0 },
    google_news: { status: "waiting", count: 0 },
    news_rss: { status: "waiting", count: 0 },
    edsurge: { status: "waiting", count: 0 },
    producthunt: { status: "waiting", count: 0 },
  });
  const [pipelineStatus, setPipelineStatus] = useState<"idle" | "running" | "complete">("idle");
  const [showAlert, setShowAlert] = useState(false);
  const [alertMessage, setAlertMessage] = useState("");

  const eventSourceRef = useRef<EventSource | null>(null);
  const feedRef = useRef<HTMLDivElement>(null);

  // Update time every second to avoid hydration mismatch
  useEffect(() => {
    setCurrentTime(new Date().toLocaleTimeString());
    const interval = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Connect to SSE stream
    const streamUrl = `${API_BASE.replace('/api', '')}/api/stream/warroom`;
    const eventSource = new EventSource(streamUrl);
    eventSourceRef.current = eventSource;
    setIsConnected(true);
    setPipelineStatus("running");

    eventSource.onmessage = (e) => {
      const event: WarRoomEvent = JSON.parse(e.data);
      handleEvent(event);
    };

    eventSource.onerror = () => {
      setIsConnected(false);
      addFeedItem("error", "Connection closed", "");
      eventSource.close();
    };

    return () => {
      eventSource.close();
      setIsConnected(false);
    };
  }, []);

  const handleEvent = (event: WarRoomEvent) => {
    switch (event.type) {
      case "start":
        addFeedItem("status", event.message || "Starting...", event.ts);
        break;

      case "status":
        addFeedItem("status", event.message || "", event.ts);
        if (event.source) {
          updateSourceStatus(event.source, "running");
        }
        break;

      case "post":
        setSignalCount((prev) => prev + 1);
        const postText = `[${event.source?.toUpperCase()}] ${event.title}`;
        addFeedItem("post", postText, event.ts);
        if (event.category) {
          updateCategoryCount(event.category);
        }
        break;

      case "source_complete":
        if (event.source) {
          updateSourceStatus(event.source, "complete", event.count);
        }
        break;

      case "category_summary":
        if (event.counts) {
          setCategoryBreakdown(event.counts as any);
        }
        break;

      case "insight":
        addFeedItem("insight", `★ ${event.text}`, event.ts);
        break;

      case "pulse":
        animatePulseScore(event.score || 0);
        break;

      case "alert":
        setAlertCount((prev) => prev + 1);
        setShowAlert(true);
        setAlertMessage(event.message || "Alert!");
        addFeedItem("alert", `🚨 ${event.message}`, event.ts);
        break;

      case "done":
        addFeedItem("status", `✓ ${event.message}`, event.ts);
        setPipelineStatus("complete");
        setIsConnected(false);
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
        }
        break;

      case "error":
        addFeedItem("error", event.message || "Error occurred", event.ts);
        break;
    }
  };

  const addFeedItem = (type: string, text: string, ts: string) => {
    const item: FeedItem = {
      type,
      text,
      ts,
      id: `${Date.now()}-${Math.random()}`,
    };
    setFeed((prev) => {
      const newFeed = [item, ...prev];
      return newFeed.slice(0, 100); // Keep max 100 items
    });
  };

  const updateSourceStatus = (source: string, status: SourceStatus["status"], count?: number) => {
    setSourceStatus((prev) => ({
      ...prev,
      [source]: {
        status,
        count: count !== undefined ? count : prev[source]?.count || 0,
      },
    }));
  };

  const updateCategoryCount = (category: string) => {
    setCategoryBreakdown((prev) => ({
      ...prev,
      [category]: (prev[category as keyof typeof prev] || 0) + 1,
    }));
  };

  const animatePulseScore = (target: number) => {
    let current = pulseScore;
    const step = Math.ceil((target - current) / 20);
    const interval = setInterval(() => {
      current = Math.min(current + step, target);
      setPulseScore(current);
      if (current >= target) {
        clearInterval(interval);
      }
    }, 30);
  };

  const handleClose = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    onClose();
  };

  const getStatusIcon = (status: SourceStatus["status"]) => {
    if (status === "complete") return "✓";
    if (status === "running") return "~";
    return "○";
  };

  const getFeedItemClass = (type: string) => {
    const base = "px-3 py-2 text-sm font-mono border-l-2 transition-colors";
    if (type === "post") return `${base} border-l-blue-400 bg-slate-800/50 text-slate-300`;
    if (type === "insight") return `${base} border-l-amber-400 bg-amber-950/30 text-amber-200`;
    if (type === "alert") return `${base} border-l-red-400 bg-red-950/30 text-red-200`;
    if (type === "status") return `${base} border-l-green-400 bg-green-950/30 text-green-200`;
    if (type === "error") return `${base} border-l-red-500 bg-red-950/50 text-red-300`;
    return `${base} border-l-slate-600 text-slate-400`;
  };

  const totalCategorySignals = Object.values(categoryBreakdown).reduce((a, b) => a + b, 0);
  const getCategoryWidth = (count: number) => {
    return totalCategorySignals > 0 ? (count / totalCategorySignals) * 100 : 0;
  };

  return (
    <div className="fixed inset-0 z-50 flex flex-col bg-[#0a0f1e] text-slate-100">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-700 bg-slate-900/50 px-6 py-4">
        <div className="flex items-center gap-4">
          <Activity className="h-6 w-6 text-blue-400" />
          <h1 className="text-xl font-bold">MORNINGPULSE WAR ROOM</h1>
          {isConnected && (
            <Badge variant="destructive" className="animate-pulse">
              LIVE
            </Badge>
          )}
          <span className="font-mono text-sm text-slate-400">{currentTime || "--:--:--"}</span>
        </div>
        <Button variant="ghost" size="icon" onClick={handleClose}>
          <X className="h-5 w-5" />
        </Button>
      </div>

      {/* Stats Bar */}
      <div className="border-b border-slate-700 bg-slate-900/30 px-6 py-3">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-400">Pulse Score:</span>
            <div className="flex items-center gap-2">
              <Progress value={pulseScore} className="h-2 w-32" />
              <span className="font-mono text-lg font-bold text-blue-400">{pulseScore}/100</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-400">Signals:</span>
            <span className="font-mono text-lg font-bold text-green-400">{signalCount}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-400">Alerts:</span>
            <span className="font-mono text-lg font-bold text-red-400">{alertCount}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-400">Status:</span>
            <Badge variant={pipelineStatus === "complete" ? "default" : "secondary"}>
              {pipelineStatus.toUpperCase()}
            </Badge>
          </div>
        </div>
      </div>

      {/* Alert Banner */}
      {showAlert && (
        <div className="border-b border-red-500 bg-red-950/50 px-6 py-3">
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-5 w-5 text-red-400" />
            <span className="font-semibold text-red-200">{alertMessage}</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAlert(false)}
              className="ml-auto text-red-300 hover:text-red-100"
            >
              Dismiss
            </Button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Live Feed */}
        <div className="flex flex-1 flex-col border-r border-slate-700">
          <div className="border-b border-slate-700 bg-slate-900/30 px-4 py-2">
            <h2 className="font-semibold text-slate-300">LIVE SIGNAL FEED</h2>
          </div>
          <div ref={feedRef} className="flex-1 space-y-1 overflow-y-auto p-2">
            {feed.map((item) => (
              <div key={item.id} className={getFeedItemClass(item.type)}>
                <span className="mr-2 text-xs text-slate-500">{item.ts}</span>
                <span>{item.text}</span>
              </div>
            ))}
            {feed.length === 0 && (
              <div className="flex h-full items-center justify-center text-slate-500">
                Waiting for signals...
              </div>
            )}
          </div>
        </div>

        {/* Right Panel */}
        <div className="flex w-96 flex-col">
          {/* Pipeline Status */}
          <Card className="m-4 border-slate-700 bg-slate-900/50 shadow-none">
            <div className="border-b border-slate-700 p-3">
              <h3 className="font-semibold text-slate-300">PIPELINE STATUS</h3>
            </div>
            <div className="space-y-2 p-3">
              {Object.entries(sourceStatus).map(([source, status]) => (
                <div key={source} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-slate-400">{getStatusIcon(status.status)}</span>
                    <span className="text-slate-300">{source.replace("_", " ")}</span>
                  </div>
                  <span className="font-mono text-slate-500">
                    {status.count > 0 ? `${status.count} posts` : status.status}
                  </span>
                </div>
              ))}
            </div>
          </Card>

          {/* Category Breakdown */}
          <Card className="m-4 mt-0 border-slate-700 bg-slate-900/50 shadow-none">
            <div className="border-b border-slate-700 p-3">
              <h3 className="font-semibold text-slate-300">CATEGORY BREAKDOWN</h3>
            </div>
            <div className="space-y-3 p-3">
              {Object.entries(categoryBreakdown).map(([category, count]) => (
                <div key={category} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className="capitalize text-slate-300">{category.replace("_", " ")}</span>
                    <span className="font-mono text-slate-400">{count}</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-slate-800">
                    <div
                      className="h-full bg-blue-500 transition-all duration-300"
                      style={{ width: `${getCategoryWidth(count)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Actions */}
          {pipelineStatus === "complete" && (
            <div className="m-4 mt-auto">
              <Button className="w-full" onClick={() => (window.location.href = "/")}>
                View Full Digest
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
