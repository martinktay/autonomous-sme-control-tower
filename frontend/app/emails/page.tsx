/**
 * @file Emails page (/emails) — Email ingestion, AI classification, task extraction, and reply drafting.
 * Supports SES-based sending and WhatsApp notification flow for high-priority emails.
 */
"use client";

import { useState } from "react";
import { ingestEmail, getEmails, generateEmailReply, sendEmail } from "@/lib/api";
import { useOrg } from "@/lib/org-context";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Mail, Send, RefreshCw, Inbox, MessageSquare, Tag, AlertCircle, CheckCircle2 } from "lucide-react";
import Link from "next/link";

interface EmailSignal {
  signal_id: string;
  content: {
    subject: string;
    body: string;
    sender: string;
    classification?: Record<string, any>;
    task_extraction?: { tasks?: Array<Record<string, any>>; email_summary?: string };
  };
  created_at?: string;
}

export default function EmailsPage() {
  const { orgId } = useOrg();
  const [emails, setEmails] = useState<EmailSignal[]>([]);
  const [loading, setLoading] = useState(false);
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [sender, setSender] = useState("");
  const [ingestResult, setIngestResult] = useState<any>(null);
  const [replyDraft, setReplyDraft] = useState<string | null>(null);
  const [replyFor, setReplyFor] = useState<string | null>(null);
  const [showCompose, setShowCompose] = useState(false);
  const [sending, setSending] = useState(false);
  const [sendResult, setSendResult] = useState<{ signalId: string; success: boolean; message: string } | null>(null);

  const handleFetch = async () => {
    setLoading(true);
    try {
      const data = await getEmails(orgId);
      setEmails(data.emails || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleIngest = async () => {
    if (!subject.trim() || !body.trim() || !sender.trim()) return;
    setLoading(true);
    try {
      const result = await ingestEmail(orgId, subject, body, sender);
      setIngestResult(result);
      setSubject("");
      setBody("");
      setSender("");
      setShowCompose(false);
      handleFetch();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleReply = async (signalId: string) => {
    setReplyFor(signalId);
    setReplyDraft(null);
    try {
      const data = await generateEmailReply(orgId, signalId);
      setReplyDraft(data.draft_reply);
    } catch {
      setReplyDraft("Failed to generate reply.");
    }
  };

  const handleSendReply = async (em: EmailSignal) => {
    if (!replyDraft || sending) return;
    setSending(true);
    setSendResult(null);
    try {
      await sendEmail(orgId, em.content.sender, `Re: ${em.content.subject}`, replyDraft);
      setSendResult({ signalId: em.signal_id, success: true, message: "Reply sent successfully" });
    } catch (e: any) {
      setSendResult({ signalId: em.signal_id, success: false, message: e.message || "Failed to send" });
    } finally {
      setSending(false);
    }
  };

  const priorityColor = (p?: string) => {
    if (p === "high") return "bg-red-100 text-red-700 border-red-200";
    if (p === "medium") return "bg-amber-50 text-amber-700 border-amber-200";
    return "bg-emerald-50 text-emerald-700 border-emerald-200";
  };

  const categoryColor = (c?: string) => {
    if (c === "payment_reminder") return "bg-orange-50 text-orange-600";
    if (c === "customer_inquiry") return "bg-blue-50 text-blue-600";
    if (c === "operational_message") return "bg-violet-50 text-violet-600";
    return "bg-slate-100 text-slate-600";
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Mail className="h-7 w-7 text-primary" />
            Email Inbox
          </h1>
          <p className="text-muted-foreground mt-1">
            Ingest business emails for AI classification, task extraction, and auto-replies.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleFetch} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Button size="sm" onClick={() => setShowCompose(!showCompose)}>
            <Send className="h-4 w-4 mr-2" />
            {showCompose ? "Cancel" : "Ingest Email"}
          </Button>
          <Link href="/emails/tasks">
            <Button variant="outline" size="sm">View Tasks</Button>
          </Link>
        </div>
      </div>

      {/* Compose / Ingest Form */}
      {showCompose && (
        <Card className="border-primary/20 bg-blue-50/30">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Ingest New Email</CardTitle>
            <CardDescription>Paste a business email to classify it and extract tasks automatically.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <input
                className="rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="Sender email"
                value={sender}
                onChange={(e) => setSender(e.target.value)}
              />
              <input
                className="rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="Subject line"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
              />
            </div>
            <textarea
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm min-h-[120px] placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="Paste the email body here..."
              value={body}
              onChange={(e) => setBody(e.target.value)}
            />
            <Button onClick={handleIngest} disabled={loading || !subject.trim() || !body.trim() || !sender.trim()}>
              {loading ? "Processing..." : "Classify & Extract Tasks"}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Ingestion Result */}
      {ingestResult && (
        <Card className="border-emerald-200 bg-emerald-50/50">
          <CardContent className="py-4">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-full bg-emerald-100 flex items-center justify-center">
                <AlertCircle className="h-4 w-4 text-emerald-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-emerald-800">Email processed successfully</p>
                <p className="text-xs text-emerald-600">
                  Category: {ingestResult.classification?.category || "N/A"} · Priority: {ingestResult.classification?.priority || "N/A"} · Tasks created: {ingestResult.tasks_created || 0}
                </p>
              </div>
              <Button variant="ghost" size="sm" onClick={() => setIngestResult(null)}>Dismiss</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Email List */}
      {emails.length === 0 && !loading && (
        <Card>
          <CardContent className="py-12 text-center space-y-3">
            <Inbox className="h-12 w-12 mx-auto text-muted-foreground/50" />
            <h3 className="font-semibold text-lg">No emails yet</h3>
            <p className="text-sm text-muted-foreground max-w-md mx-auto">
              Click &quot;Ingest Email&quot; to paste a business email, or click Refresh to load existing ones.
            </p>
          </CardContent>
        </Card>
      )}

      <div className="space-y-3">
        {emails.map((em) => {
          const cls = em.content.classification || {};
          const tasks = em.content.task_extraction?.tasks || [];
          return (
            <Card key={em.signal_id} className="hover:shadow-sm transition-shadow">
              <CardContent className="py-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{em.content.subject}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">From: {em.content.sender}</p>
                  </div>
                  <div className="flex gap-1.5 ml-3 shrink-0">
                    {cls.priority && (
                      <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${priorityColor(cls.priority)}`}>
                        {cls.priority}
                      </span>
                    )}
                    {cls.category && (
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${categoryColor(cls.category)}`}>
                        <Tag className="h-3 w-3 inline mr-1" />
                        {cls.category.replace(/_/g, " ")}
                      </span>
                    )}
                  </div>
                </div>

                <p className="text-sm text-muted-foreground mb-3 line-clamp-2">{em.content.body}</p>

                {cls.summary && (
                  <p className="text-xs text-muted-foreground italic mb-3 bg-muted/50 rounded px-2 py-1">
                    {cls.summary}
                  </p>
                )}

                {tasks.length > 0 && (
                  <div className="mb-3">
                    <p className="text-xs font-medium text-muted-foreground mb-1">Extracted tasks:</p>
                    <div className="flex flex-wrap gap-1">
                      {tasks.map((t: any, i: number) => (
                        <span key={i} className="inline-block bg-primary/10 text-primary text-xs rounded-full px-2.5 py-0.5 font-medium">
                          {t.title}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <Button variant="ghost" size="sm" onClick={() => handleReply(em.signal_id)} className="text-xs">
                  <MessageSquare className="h-3.5 w-3.5 mr-1.5" />
                  Generate Reply Draft
                </Button>

                {replyFor === em.signal_id && replyDraft && (
                  <div className="mt-3 space-y-2">
                    <div className="bg-muted/50 rounded-md p-3 text-sm text-foreground whitespace-pre-wrap border">
                      {replyDraft}
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        onClick={() => handleSendReply(em)}
                        disabled={sending}
                        className="text-xs"
                      >
                        <Send className="h-3.5 w-3.5 mr-1.5" />
                        {sending ? "Sending..." : "Send via SES"}
                      </Button>
                      {sendResult && sendResult.signalId === em.signal_id && (
                        <span className={`text-xs flex items-center gap-1 ${sendResult.success ? "text-emerald-600" : "text-red-600"}`}>
                          {sendResult.success ? <CheckCircle2 className="h-3.5 w-3.5" /> : <AlertCircle className="h-3.5 w-3.5" />}
                          {sendResult.message}
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
