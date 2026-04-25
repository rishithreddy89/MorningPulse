import { useState, useRef, useEffect } from "react";
import { MessageCircle, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ChatPanel } from "@/components/ChatPanel";

export function FloatingChat({ date }: { date?: string }) {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const chatRef = useRef<HTMLDivElement>(null);

  // Close chat when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (chatRef.current && !chatRef.current.contains(event.target as Node)) {
        setIsChatOpen(false);
      }
    };

    if (isChatOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isChatOpen]);

  // Close on Escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape" && isChatOpen) {
        setIsChatOpen(false);
      }
    };

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isChatOpen]);

  return (
    <>
      {/* Chat Panel - Floating */}
      <div
        ref={chatRef}
        className={`
          fixed bottom-24 right-6 z-50
          w-[380px] h-[600px]
          transition-all duration-300 ease-out
          ${
            isChatOpen
              ? "opacity-100 translate-y-0 pointer-events-auto"
              : "opacity-0 translate-y-4 pointer-events-none"
          }
          max-md:w-[calc(100vw-2rem)] max-md:h-[calc(100vh-8rem)]
          max-md:bottom-20 max-md:right-4 max-md:left-4
        `}
        style={{
          boxShadow: isChatOpen ? "0 8px 32px rgba(0, 0, 0, 0.12)" : "none",
        }}
      >
        <div className="relative h-full rounded-xl overflow-hidden bg-background border border-border">
          {/* Close button */}
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-3 right-3 z-10 h-8 w-8 rounded-full"
            onClick={() => setIsChatOpen(false)}
          >
            <X className="h-4 w-4" />
          </Button>

          {/* Chat Panel */}
          <ChatPanel date={date} />
        </div>
      </div>

      {/* Chat Button - Fixed Bottom Right */}
      <Button
        onClick={() => setIsChatOpen((prev) => !prev)}
        size="icon"
        className={`
          fixed bottom-6 right-6 z-50
          h-14 w-14 rounded-full
          shadow-lg hover:shadow-xl
          transition-all duration-300
          ${isChatOpen ? "rotate-0 scale-90" : "rotate-0 scale-100"}
        `}
        aria-label={isChatOpen ? "Close chat" : "Open chat"}
      >
        <MessageCircle
          className={`
            h-6 w-6 transition-transform duration-300
            ${isChatOpen ? "scale-0" : "scale-100"}
          `}
        />
        <X
          className={`
            absolute h-6 w-6 transition-transform duration-300
            ${isChatOpen ? "scale-100" : "scale-0"}
          `}
        />
      </Button>

      {/* Notification Badge (optional - can be enabled later) */}
      {!isChatOpen && false && (
        <div className="fixed bottom-[4.5rem] right-[4.5rem] z-50 h-5 w-5 rounded-full bg-destructive border-2 border-background flex items-center justify-center">
          <span className="text-[10px] font-bold text-destructive-foreground">1</span>
        </div>
      )}
    </>
  );
}
