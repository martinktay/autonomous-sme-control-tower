#!/usr/bin/env python3
import os

CONTENT = r'''"use client";

import { useState } from "react";
import { ingestEmail, getEmails, generateEmailReply } from "@/lib/api";

const ORG_ID = "org_demo";

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
  const [emails, setEmails] = useState<EmailSignal[]>([]);
  const [loading, setLoading] = useState(false);
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [sender, setSender] = useState("");
  const [ingestResult, setIngestResult] = useState<any>(null);
  const [replyDraft, setReplyDraft] = useState<string | null>(null);
  const [replyFor, setReplyFor] = useState<string | null>(null);

  const handleFetch = async () => {
    setLoading(true);
    try {
      const data = await getEmails(ORG_ID);
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
      const result = await ingestEmail(ORG_ID, subject, body, sender);
      setIngestResult(result);
      setSubject("");
      setBody("");
      setSender("");
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
      const data = await generateEmailReply(ORG_ID, signalId);
      setReplyDraft(data.draft_reply);
    } catch {
      setReplyDraft("Failed to generate reply.");
    }
  };

  const priorityColor = (p?: string) => {
    if (p === "high") return "text-red-400";
    if (p === "medium") return "text-yellow-400";
    return "text-green-400";
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Email Inbox &amp; Ingestion</h1>

      <div className="bg-gray-900 rounded-lg p-4 mb-6 border border-gray-800">
        <h2 className="text-lg font-semibold mb-3">Ingest New Email</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
          <input className="bg-gray-800 rounded px-3 py-2 text-sm" placeholder="Sender email" value={sender} onChange={(e) => setSender(e.target.value)} />
          <input className="bg-gray-800 rounded px-3 py-2 text-sm" placeholder="Subject" value={subject} onChange={(e) => setSubject(e.target.value)} />
        </div>
        <textarea className="w-full bg-gray-800 rounded px-3 py-2 text-sm mb-3 min-h-[100px]" placeholder="Email body..." value={body} onChange={(e) => setBody(e.target.value)} />
        <button onClick={handleIngest} disabled={loading} className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm disabled:opacity-50">
          {loading ? "Processing..." : "Ingest Email"}
        </button>
      </div>

      {ingestResult && (
        <div className="bg-gray-900 rounded-lg p-4 mb-6 border border-green-800">
          <h3 className="font-semibold text-green-400 mb-2">Ingestion Result</h3>
          <p className="text-sm text-gray-300">Category: {ingestResult.classification?.category || "N/A"}</p>
          <p className="text-sm text-gray-300">Priority: {ingestResult.classification?.priority || "N/A"}</p>
          <p className="text-sm text-gray-300">Tasks created: {ingestResult.tasks_created || 0}</p>
        </div>
      )}

      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Ingested Emails</h2>
        <button onClick={handleFetch} disabled={loading} className="bg-gray-800 hover:bg-gray-700 px-3 py-1.5 rounded text-sm disabled:opacity-50">
          {loading ? "Loading..." : "Refresh"}
        </button>
      </div>

      {emails.length === 0 && !loading && (
        <p className="text-gray-500 text-sm">No emails yet. Ingest one above or click Refresh.</p>
      )}

      <div className="space-y-3">
        {emails.map((em) => {
          const cls = em.content.classification || {};
          const tasks = em.content.task_extraction?.tasks || [];
          return (
            <div key={em.signal_id} className="bg-gray-900 rounded-lg p-4 border border-gray-800">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <p className="font-medium">{em.content.subject}</p>
                  <p className="text-xs text-gray-400">From: {em.content.sender}</p>
                </div>
                <div className="text-right text-xs">
                  <span className={`font-medium ${priorityColor(cls.priority)}`}>{cls.priority || "\u2014"}</span>
                  <span className="ml-2 text-gray-500">{cls.category || ""}</span>
                </div>
              </div>
              <p className="text-sm text-gray-300 mb-2 line-clamp-2">{em.content.body}</p>
              {cls.summary && <p className="text-xs text-gray-400 italic mb-2">{cls.summary}</p>}
              {tasks.length > 0 && (
                <div className="mb-2">
                  <p className="text-xs text-gray-500 mb-1">Extracted tasks:</p>
                  {tasks.map((t: any, i: number) => (
                    <span key={i} className="inline-block bg-gray-800 text-xs rounded px-2 py-0.5 mr-1 mb-1">{t.title}</span>
                  ))}
                </div>
              )}
              <button onClick={() => handleReply(em.signal_id)} className="text-xs text-blue-400 hover:text-blue-300">
                Generate Reply Draft
              </button>
              {replyFor === em.signal_id && replyDraft && (
                <div className="mt-2 bg-gray-800 rounded p-3 text-sm text-gray-300 whitespace-pre-wrap">{replyDraft}</div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
'''

target = os.path.join(os.path.dirname(__file__), 'page.tsx')
with open(target, 'w', encoding='utf-8') as f:
    f.write(CONTENT)
    f.flush()
    os.fsync(f.fileno())

print(f"Written {os.path.getsize(target)} bytes to {target}")
