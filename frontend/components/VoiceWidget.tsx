"use client"

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getVoiceSummary } from "@/lib/api";

export default function VoiceWidget({ orgId = "org_default" }: { orgId?: string }) {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const data = await getVoiceSummary(orgId);
      setResponse(data.summary || "No summary available.");
    } catch {
      setResponse("Failed to get summary.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-lg border p-4 space-y-3">
      <h3 className="font-semibold text-sm">Voice Query</h3>
      <div className="flex gap-2">
        <Input
          placeholder="Ask about your business..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
        />
        <Button
          size="sm"
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? "..." : "Ask"}
        </Button>
      </div>
      {response && (
        <p className="text-sm text-muted-foreground whitespace-pre-wrap">{response}</p>
      )}
    </div>
  );
}
