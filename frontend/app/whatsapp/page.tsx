/**
 * @file WhatsApp integration page — ingest messages and view AI-generated summaries.
 * Allows manual message ingestion for testing and displays processed messages.
 */
"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  ingestWhatsAppMessage,
  getWhatsAppSummary,
  getWhatsAppMessages,
} from "@/lib/api";
import { useOrg } from "@/lib/org-context";
import { formatRelative } from "@/lib/format-date";
import CurrencyDisplay from "@/components/CurrencyDisplay";
import {
  MessageCircle,
  Send,
  Loader2,
  Sparkles,
  Phone,
  ShoppingCart,
  Receipt,
  HelpCircle,
} from "lucide-react";

const typeIcons: Record<string, typeof Receipt> = {
  invoice: Receipt,
  receipt: Receipt,
  payment: ShoppingCart,
  order: ShoppingCart,
  stock_update: ShoppingCart,
  inquiry: HelpCircle,
};

export default function WhatsAppPage() {
  const { orgId, orgName } = useOrg();
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [messageText, setMessageText] = useState("");
  const [senderName, setSenderName] = useState("");
  const [sending, setSending] = useState(false);
  const [summary, setSummary] = useState<any>(null);
  const [summaryText, setSummaryText] = useState("");
  const [generatingSummary, setGeneratingSummary] = useState(false);

  useEffect(() => {
    if (!orgId) return;
    setLoading(true);
    getWhatsAppMessages(orgId)
      .then((res) => setMessages(res.messages || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [orgId]);

  const handleSend = async () => {
    if (!messageText.trim()) return;
    setSending(true);
    try {
      const res = await ingestWhatsAppMessage(
        orgId,
        messageText,
        senderName || undefined,
      );
      setMessages((prev) => [
        { signal_id: res.signal_id, content: res.extracted_data, created_at: new Date().toISOString() },
        ...prev,
      ]);
      setMessageText("");
      setSenderName("");
    } catch {
      /* swallow */
    } finally {
      setSending(false);
    }
  };

  const handleGenerateSummary = async () => {
    setGeneratingSummary(true);
    try {
      const res = await getWhatsAppSummary(orgId, orgName);
      setSummary(res.summary);
      setSummaryText(res.formatted_text);
    } catch {
      setSummaryText("Could not generate summary right now.");
    } finally {
      setGeneratingSummary(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="flex items-center gap-3 mb-6">
        <MessageCircle className="h-6 w-6 text-green-600" />
        <div>
          <h1 className="text-2xl font-bold">WhatsApp</h1>
          <p className="text-sm text-muted-foreground">
            Send business messages for AI extraction, or get a daily summary
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Ingest + Messages */}
        <div className="space-y-4">
          {/* Message input */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Paste a WhatsApp message</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <input
                placeholder="Sender name (optional)"
                value={senderName}
                onChange={(e) => setSenderName(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm bg-background"
              />
              <textarea
                placeholder="Paste the WhatsApp message here... e.g. 'Oga, your 50 bags of rice don arrive. Total: 750k. Pay before Friday.'"
                value={messageText}
                onChange={(e) => setMessageText(e.target.value)}
                rows={4}
                className="w-full border rounded-lg px-3 py-2 text-sm bg-background resize-none"
              />
              <Button
                onClick={handleSend}
                disabled={sending || !messageText.trim()}
                className="w-full"
                size="sm"
              >
                {sending ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Send className="h-4 w-4 mr-2" />
                )}
                {sending ? "Processing..." : "Process Message"}
              </Button>
            </CardContent>
          </Card>

          {/* Message history */}
          <div className="space-y-2">
            <p className="text-sm font-medium text-muted-foreground">
              {messages.length} processed message{messages.length !== 1 ? "s" : ""}
            </p>
            {loading ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
              </div>
            ) : messages.length === 0 ? (
              <Card>
                <CardContent className="py-8 text-center text-sm text-muted-foreground">
                  No WhatsApp messages yet. Paste one above to get started.
                </CardContent>
              </Card>
            ) : (
              messages.map((msg: any) => {
                const c = msg.content || {};
                const Icon = typeIcons[c.message_type] || MessageCircle;
                return (
                  <Card key={msg.signal_id}>
                    <CardContent className="py-3">
                      <div className="flex items-start gap-3">
                        <div className="p-1.5 rounded-lg bg-green-50">
                          <Icon className="h-4 w-4 text-green-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-xs px-2 py-0.5 rounded-full bg-muted capitalize">
                              {c.message_type || "message"}
                            </span>
                            {c.sender_name && (
                              <span className="text-xs text-muted-foreground">{c.sender_name}</span>
                            )}
                            <span className="text-xs text-muted-foreground ml-auto">
                              {formatRelative(msg.created_at)}
                            </span>
                          </div>
                          <p className="text-sm mt-1">{c.description || c.raw_message?.slice(0, 100) || "—"}</p>
                          {c.amount != null && (
                            <div className="mt-1">
                              <CurrencyDisplay amount={c.amount} currency={c.currency || "NGN"} className="text-sm font-medium" />
                            </div>
                          )}
                          {c.action_required && (
                            <p className="text-xs text-primary mt-1">→ {c.action_required}</p>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })
            )}
          </div>
        </div>

        {/* Right: Daily Summary */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm font-medium">
                <Sparkles className="h-4 w-4 text-yellow-500" />
                Daily Business Summary
              </CardTitle>
              <p className="text-xs text-muted-foreground">
                Generate a WhatsApp-ready summary of your business health
              </p>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button
                onClick={handleGenerateSummary}
                disabled={generatingSummary}
                variant="outline"
                className="w-full"
                size="sm"
              >
                {generatingSummary ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Phone className="h-4 w-4 mr-2" />
                )}
                {generatingSummary ? "Generating..." : "Generate Summary"}
              </Button>

              {summaryText && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <pre className="text-sm whitespace-pre-wrap font-sans leading-relaxed">
                    {summaryText}
                  </pre>
                  <button
                    onClick={() => navigator.clipboard.writeText(summaryText)}
                    className="mt-2 text-xs text-green-700 hover:underline"
                  >
                    Copy to clipboard
                  </button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
