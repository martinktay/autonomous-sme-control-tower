/**
 * InsightsPanel — Displays AI-generated business insights including
 * a plain-language summary, colour-coded highlights, and recommended next steps.
 * Users can trigger insight generation on demand via the "Get Insights" button.
 */
"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Sparkles,
  TrendingUp,
  AlertTriangle,
  AlertCircle,
  Loader2,
  Lightbulb,
  ChevronRight,
} from "lucide-react";

interface Highlight {
  type: "positive" | "warning" | "critical";
  title: string;
  detail: string;
}

interface InsightsData {
  summary: string;
  highlights: Highlight[];
  next_steps: string[];
  confidence: string;
}

interface InsightsPanelProps {
  insights: InsightsData | null;
  loading: boolean;
  onGenerate: () => void;
  generating: boolean;
}

export default function InsightsPanel({
  insights,
  loading,
  onGenerate,
  generating,
}: InsightsPanelProps) {
  const getHighlightIcon = (type: string) => {
    switch (type) {
      case "positive":
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case "critical":
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      case "warning":
        return <AlertCircle className="h-4 w-4 text-yellow-600" />;
      default:
        return <Lightbulb className="h-4 w-4 text-blue-600" />;
    }
  };

  const getHighlightBorder = (type: string) => {
    switch (type) {
      case "positive":
        return "border-l-green-500";
      case "critical":
        return "border-l-red-500";
      case "warning":
        return "border-l-yellow-500";
      default:
        return "border-l-blue-500";
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            <CardTitle>AI Business Insights</CardTitle>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={onGenerate}
            disabled={generating || loading}
          >
            {generating ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Sparkles className="h-4 w-4 mr-2" />
            )}
            {generating ? "Analysing..." : "Get Insights"}
          </Button>
        </div>
        <CardDescription>
          Click &quot;Get Insights&quot; for a plain-language summary of how your business is doing, what needs attention, and what to do next — written so anyone can understand it, no accounting degree needed.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center gap-2 text-muted-foreground py-4">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">Loading insights…</span>
          </div>
        ) : !insights ? (
          <div className="text-center py-6">
            <Sparkles className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
            <p className="text-sm font-medium">No insights yet</p>
            <p className="text-xs text-muted-foreground mt-1">
              Click &quot;Get Insights&quot; to have AI analyse your business data and
              explain what&apos;s happening in plain language.
            </p>
          </div>
        ) : (
          <div className="space-y-5">
            {/* Summary */}
            <div className="rounded-lg bg-primary/5 p-4">
              <p className="text-sm leading-relaxed">{insights.summary}</p>
            </div>

            {/* Highlights */}
            {insights.highlights.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                  Key Findings
                </p>
                {insights.highlights.map((h, i) => (
                  <div
                    key={i}
                    className={`border-l-4 ${getHighlightBorder(h.type)} rounded-r-lg bg-card p-3 flex items-start gap-3`}
                  >
                    <div className="mt-0.5">{getHighlightIcon(h.type)}</div>
                    <div>
                      <p className="text-sm font-medium">{h.title}</p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {h.detail}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Next Steps */}
            {insights.next_steps.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                  Recommended Next Steps
                </p>
                {insights.next_steps.map((step, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <ChevronRight className="h-4 w-4 text-primary mt-0.5 shrink-0" />
                    <p className="text-sm">{step}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
