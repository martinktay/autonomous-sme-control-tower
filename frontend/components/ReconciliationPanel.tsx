"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { reconcileDocuments } from "@/lib/api";
import { useOrg } from "@/lib/org-context";
import { Upload, Loader2 } from "lucide-react";

export default function ReconciliationPanel() {
  const { orgId } = useOrg();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleReconcile = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const res = await reconcileDocuments(orgId, file);
      setResult(res.reconciliation);
    } catch { setResult(null); }
    finally { setLoading(false); }
  };

  const summary = result?.summary;

  return (
    <Card>
      <CardHeader><CardTitle>Bank Reconciliation</CardTitle></CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">
          Upload a bank statement (CSV or Excel) with columns: date, description, amount. The system matches transactions against your documents.
        </p>
        <div className="flex gap-3 items-end">
          <div className="flex-1">
            <input type="file" accept=".csv,.xls,.xlsx" onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="text-sm" aria-label="Bank statement file" />
          </div>
          <Button onClick={handleReconcile} disabled={!file || loading} className="gap-2">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
            Reconcile
          </Button>
        </div>

        {result && summary && (
          <div className="space-y-3">
            <div className="grid grid-cols-3 gap-3 text-center text-sm">
              <div className="bg-muted rounded p-3">
                <p className="text-muted-foreground">Total Transactions</p>
                <p className="text-lg font-semibold">{summary.total_transactions}</p>
              </div>
              <div className="bg-green-50 rounded p-3">
                <p className="text-green-700">Matched</p>
                <p className="text-lg font-semibold text-green-700">{summary.matched_count}</p>
              </div>
              <div className="bg-red-50 rounded p-3">
                <p className="text-red-700">Unmatched Txns</p>
                <p className="text-lg font-semibold text-red-700">{summary.unmatched_transaction_count}</p>
              </div>
            </div>

            {result.unmatched_transactions?.length > 0 && (
              <div>
                <p className="text-sm font-medium mb-2">Unmatched Bank Transactions</p>
                <div className="space-y-1">
                  {result.unmatched_transactions.map((t: any, i: number) => (
                    <div key={i} className="flex justify-between text-xs bg-muted rounded px-3 py-2">
                      <span>{t.date} — {t.description}</span>
                      <Badge variant="outline">{t.amount}</Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
