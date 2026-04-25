import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Play, Pause, Square, Copy, Volume2 } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface VoiceDigestProps {
  digest: any;
}

export function VoiceDigest({ digest }: VoiceDigestProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [totalDuration, setTotalDuration] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [selectedVoice, setSelectedVoice] = useState<string>("");
  const [availableVoices, setAvailableVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [script, setScript] = useState("");

  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const progressIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<number>(0);
  const pausedTimeRef = useRef<number>(0);

  // Load available voices
  useEffect(() => {
    const loadVoices = () => {
      const voices = window.speechSynthesis.getVoices();
      setAvailableVoices(voices);
      
      // Select default voice (prefer English voices)
      const defaultVoice = voices.find(v => v.lang.startsWith("en")) || voices[0];
      if (defaultVoice) {
        setSelectedVoice(defaultVoice.name);
      }
    };

    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;

    return () => {
      window.speechSynthesis.onvoiceschanged = null;
    };
  }, []);

  // Build script from digest
  useEffect(() => {
    if (digest) {
      const builtScript = buildScript(digest);
      setScript(builtScript);
      
      // Estimate duration (rough: 150 words per minute)
      const wordCount = builtScript.split(/\s+/).length;
      const estimatedSeconds = (wordCount / 150) * 60;
      setTotalDuration(estimatedSeconds);
    }
  }, [digest]);

  const buildScript = (digest: any): string => {
    const sections: string[] = [];

    // Helper to clean text
    const cleanText = (text: string): string => {
      return text
        .replace(/[*_#`]/g, "") // Remove markdown
        .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1") // Remove markdown links
        .replace(/https?:\/\/[^\s]+/g, "") // Remove URLs
        .replace(/&/g, "and")
        .replace(/%/g, "percent")
        .replace(/\//g, " or ")
        .replace(/\s+/g, " ")
        .trim();
    };

    // INTRO
    const today = new Date().toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });
    sections.push(
      `Good morning. Here is your MorningPulse intelligence brief for ${today}.`
    );
    sections.push(" . "); // Pause

    // COMPETITOR UPDATES
    const competitors = digest?.competitor_updates || [];
    if (competitors.length > 0) {
      sections.push(
        `Competitor Updates. ${competitors.length} competitor ${
          competitors.length === 1 ? "signal" : "signals"
        } detected today.`
      );
      
      competitors.slice(0, 10).forEach((comp: any) => {
        const name = cleanText(comp.competitor_name || "Unknown competitor");
        const title = cleanText(comp.title || "");
        const description = cleanText(comp.description || "");
        
        if (title && description) {
          sections.push(`${name}. ${title}. ${description}`);
        } else if (title) {
          sections.push(`${name}. ${title}.`);
        }
      });
      
      sections.push(" . "); // Pause
    }

    // EMERGING TRENDS
    const trends = digest?.emerging_tech_trends || [];
    if (trends.length > 0) {
      sections.push("Emerging Market Signals.");
      
      trends.slice(0, 10).forEach((trend: any) => {
        const trendName = cleanText(trend.trend || "");
        const explanation = cleanText(trend.explanation || "");
        
        if (trendName && explanation) {
          sections.push(`${trendName}. ${explanation}`);
        } else if (trendName) {
          sections.push(`${trendName}.`);
        }
      });
      
      sections.push(" . "); // Pause
    }

    // USER PAIN POINTS
    const painPoints = digest?.user_pain_points || [];
    if (painPoints.length > 0) {
      sections.push(
        "User Pain Points. Educators are reporting the following frustrations."
      );
      
      painPoints.slice(0, 10).forEach((point: any) => {
        const issue = cleanText(point.issue || "");
        const context = cleanText(point.context || "");
        
        if (issue && context) {
          sections.push(`${issue}. ${context}`);
        } else if (issue) {
          sections.push(`${issue}.`);
        }
      });
      
      sections.push(" . "); // Pause
    }

    // BATTLE CARDS (if available)
    const battleCards = digest?.battle_cards || [];
    if (battleCards.length > 0) {
      sections.push("Competitive Intelligence.");
      
      battleCards.slice(0, 5).forEach((card: any) => {
        const name = cleanText(card.competitor_name || "");
        const advantage = cleanText(card.campus_cortex_advantage || "");
        
        if (name && advantage) {
          sections.push(`${name}. Our advantage: ${advantage}`);
        }
      });
      
      sections.push(" . "); // Pause
    }

    // OUTRO
    sections.push(
      "That concludes today's MorningPulse brief. Have a focused and strategic day."
    );

    return sections.join(" ");
  };

  const handlePlay = () => {
    if (!script) return;

    if (isPaused && utteranceRef.current) {
      // Resume
      window.speechSynthesis.resume();
      setIsPaused(false);
      setIsPlaying(true);
      startProgressTracking();
    } else {
      // Start new
      const utterance = new SpeechSynthesisUtterance(script);
      
      // Set voice
      const voice = availableVoices.find(v => v.name === selectedVoice);
      if (voice) {
        utterance.voice = voice;
      }
      
      // Set rate
      utterance.rate = playbackRate;
      utterance.pitch = 1;
      utterance.volume = 1;

      // Event handlers
      utterance.onstart = () => {
        setIsPlaying(true);
        setIsPaused(false);
        startTimeRef.current = Date.now();
        startProgressTracking();
      };

      utterance.onend = () => {
        setIsPlaying(false);
        setIsPaused(false);
        setProgress(100);
        setCurrentTime(totalDuration);
        stopProgressTracking();
      };

      utterance.onerror = (event) => {
        console.error("Speech synthesis error:", event);
        setIsPlaying(false);
        setIsPaused(false);
        stopProgressTracking();
      };

      utteranceRef.current = utterance;
      window.speechSynthesis.speak(utterance);
    }
  };

  const handlePause = () => {
    if (isPlaying) {
      window.speechSynthesis.pause();
      setIsPaused(true);
      setIsPlaying(false);
      pausedTimeRef.current = currentTime;
      stopProgressTracking();
    }
  };

  const handleStop = () => {
    window.speechSynthesis.cancel();
    setIsPlaying(false);
    setIsPaused(false);
    setProgress(0);
    setCurrentTime(0);
    stopProgressTracking();
    utteranceRef.current = null;
  };

  const startProgressTracking = () => {
    stopProgressTracking();
    
    progressIntervalRef.current = setInterval(() => {
      if (totalDuration > 0) {
        const elapsed = (Date.now() - startTimeRef.current) / 1000;
        const adjustedElapsed = pausedTimeRef.current + elapsed;
        const newProgress = Math.min((adjustedElapsed / totalDuration) * 100, 100);
        
        setProgress(newProgress);
        setCurrentTime(adjustedElapsed);
      }
    }, 100);
  };

  const stopProgressTracking = () => {
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current);
      progressIntervalRef.current = null;
    }
  };

  const handleSpeedChange = (rate: number) => {
    setPlaybackRate(rate);
    
    // If currently playing, restart with new rate
    if (isPlaying || isPaused) {
      const wasPlaying = isPlaying;
      handleStop();
      
      setTimeout(() => {
        if (wasPlaying) {
          handlePlay();
        }
      }, 100);
    }
  };

  const handleVoiceChange = (voiceName: string) => {
    setSelectedVoice(voiceName);
    
    // If currently playing, restart with new voice
    if (isPlaying || isPaused) {
      const wasPlaying = isPlaying;
      handleStop();
      
      setTimeout(() => {
        if (wasPlaying) {
          handlePlay();
        }
      }, 100);
    }
  };

  const handleCopyScript = () => {
    navigator.clipboard.writeText(script);
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      handleStop();
    };
  }, []);

  if (!digest) {
    return null;
  }

  return (
    <Card className="border-border p-6 shadow-none">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center gap-2">
          <Volume2 className="h-5 w-5 text-primary" />
          <h3 className="text-lg font-semibold text-foreground">Morning Brief</h3>
        </div>

        {/* Controls */}
        <div className="flex flex-wrap items-center gap-2">
          <Button
            onClick={handlePlay}
            disabled={isPlaying}
            size="sm"
            variant={isPlaying ? "secondary" : "default"}
          >
            <Play className="mr-2 h-4 w-4" />
            Play
          </Button>
          
          <Button
            onClick={handlePause}
            disabled={!isPlaying}
            size="sm"
            variant="outline"
          >
            <Pause className="mr-2 h-4 w-4" />
            Pause
          </Button>
          
          <Button
            onClick={handleStop}
            disabled={!isPlaying && !isPaused}
            size="sm"
            variant="outline"
          >
            <Square className="mr-2 h-4 w-4" />
            Stop
          </Button>

          <Button
            onClick={handleCopyScript}
            size="sm"
            variant="ghost"
          >
            <Copy className="mr-2 h-4 w-4" />
            Copy Script
          </Button>
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
            <div
              className="h-full bg-primary transition-all duration-100"
              style={{ width: `${progress}%` }}
            />
          </div>
          
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(totalDuration)}</span>
          </div>
        </div>

        {/* Speed and Voice Controls */}
        <div className="flex flex-wrap items-center gap-4">
          {/* Speed */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Speed:</span>
            <div className="flex gap-1">
              {[0.75, 1, 1.25, 1.5].map((rate) => (
                <Button
                  key={rate}
                  onClick={() => handleSpeedChange(rate)}
                  size="sm"
                  variant={playbackRate === rate ? "default" : "outline"}
                  className="h-8 px-3"
                >
                  {rate}x
                </Button>
              ))}
            </div>
          </div>

          {/* Voice Selector */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Voice:</span>
            <Select value={selectedVoice} onValueChange={handleVoiceChange}>
              <SelectTrigger className="h-8 w-[200px]">
                <SelectValue placeholder="Select voice" />
              </SelectTrigger>
              <SelectContent>
                {availableVoices
                  .filter(v => v.lang.startsWith("en"))
                  .map((voice) => (
                    <SelectItem key={voice.name} value={voice.name}>
                      {voice.name} ({voice.lang})
                    </SelectItem>
                  ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Info */}
        <p className="text-xs text-muted-foreground">
          {script.split(/\s+/).length} words • Estimated {formatTime(totalDuration)} duration
        </p>
      </div>
    </Card>
  );
}
