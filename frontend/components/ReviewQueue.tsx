"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { getReviewQueue, updateReviewStatus } from "@/lib/api";
import { useOrg } from "@/lib/org-context";
import { CheckCircle2, XCircle, Pencil, Loader2 } from "lucide-react";

export default function ReviewQueue() {
  const { orgId } = useOrg();
  const [docs, setDocs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editFields, setEditFields] = useState<Record<string, any>>({});
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const fetchQueue = async () => {
    setLoading(true);
    try {
      const res = await getReviewQueue(orgId);
      setDocs(res.review_queue || []);
    } catch { setDocs([]); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchQueue(); }, [orgId]);

  const handleAction = async (signalId: string, action: string, edits?: Record<string, any>) => {
    setActionLoading(signalId);
    try {
      await updateReviewStatus(orgId, signalId, action, edits);
      setEditingId(null);
      await fetchQueue();
    } catch { /* ignore */ }
    finally { setActionLoading(null); }
  };

  const startEdit = (doc: any) => {
    const c = doc.content || {};
    setEditingId(doc.signal_id);
    setEditFields({ vendor_name: c.vendor_name || "", amount: c.amount || 0, category: c.category || "expense" });
  };

  if (loading) return <p className="text-sm text-muted-foreground">Loading review queue...</p>;
  if (docs.length === 0) return <p className="text-sm text-muted-foreground">No documents pending review.</p>;

  return (
    <div className="space-y-4">
      {docs.map((doc: any) => {
        const c = doc.content || {};
        const isEditing = editingId === doc.signal_id;
        const isLoading = actionLoading === doc.signal_id;
        const flags = c.flags || [];

        return (
          <Card key={doc.signal_id}>
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center justify-between">
                <span>{c.vendor_name || "Unknown Vendor"}</span>
                <Badge variant="outline">{c.currency} {c.amount}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                <span>Category: {c.category}</span>
                <span>Confidence: {((c.confidence_score || 0) * 100).toFixed(0)}%</span>
                <span>Date: {c.document_date}</span>
              </div>

              {flags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {flags.map((f: any, i: number) => (
                    <Badge key={i} variant="destructive" className="text-xs">{f.flag_reason}</Badge>
                  ))}
                </div>
              )}

              {isEditing ? (
                <div className="space-y-2 border rounded p-3">
                  <label className="block text-xs">
                    Vendor
                    <Input value={editFields.vendor_name} onChange={(e) => setEditFields({ ...editFields, vendor_name: e.target.value })} />
                  </label>
                  <label className="block text-xs">
                    Amount
                    <Input type="number" value={editFields.amount} onChange={(e) => setEditFields({ ...editFields, amount: parseFloat(e.target.value) || 0 })} />
                  </label>
                  <label className="block text-xs">
                    Category
                    <select value={editFields.category} onChange={(e) => setEditFields({ ...editFields, category: e.target.value })}
                      className="w-full border rounded px-2 py-1 text-sm">
                      <option value="revenue">Revenue</option>
                      <option value="expense">Expense</option>
                    </select>
                  </label>
                  <div className="flex gap-2">
                    <Button size="sm" onClick={() => handleAction(doc.signal_id, "edit", editFields)} disabled={isLoading}>
                      {isLoading ? <Loader2 className="h-3 w-3 animate-spin" /> : "Save"}
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => setEditingId(null)}>Cancel</Button>
                  </div>
                </div>
              ) : (
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" className="gap-1" onClick={() => handleAction(doc.signal_id, "approve")} disabled={isLoading}>
                    <CheckCircle2 className="h-3 w-3" /> Approve
                  </Button>
                  <Button size="sm" variant="outline" className="gap-1 text-destructive" onClick={() => handleAction(doc.signal_id, "reject")} disabled={isLoading}>
                    <XCircle className="h-3 w-3" /> Reject
                  </Button>
                  <Button size="sm" variant="outline" className="gap-1" onClick={() => startEdit(doc)} disabled={isLoading}>
                    <Pencil className="h-3 w-3" /> Edit
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
