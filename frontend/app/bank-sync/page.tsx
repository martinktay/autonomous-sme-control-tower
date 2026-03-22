"use client";

import { useState, useEffect } from "react";
import { useOrg } from "@/lib/org-context";
import { importBankStatement, getSupportedBanks } from "@/lib/api";
import { Landmark, Upload, CheckCircle, AlertCircle, Loader2 } from "lucide-react";

export default function BankSyncPage() {
  const { orgId } = useOrg();
  const [file, setFile] = useState<File | null>(null);
  const [banks, setBanks] = useState<any[]>([]);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getSupportedBanks()
      .then((data) => setBanks(data.supported_formats || []))
      .catch(() => {});
  }, []);

  const handleImport = async () => {
    if (!file || !orgId) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await importBankStatement(orgId, file);
      setResult(data);
    } catch (e: any) {
      setError(e.message || "Import failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <div className="flex items-center gap-3 mb-6">
        <Landmark className="h-6 w-6 text-primary" />
        <h1 className="text-2xl font-semibold">Bank Sync</h1>
      </div>
      <p className="text-muted-foreground mb-6">
        Import your bank statement to automatically reconcile against your business records. Our AI matches entries and flags discrepancies.
      </p>

      <div className="border rounded-lg p-6 mb-6 bg-card">
        <h2 className="font-medium mb-4">Import Bank Statement</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm mb-1 text-muted-foreground">Supported Banks</label>
            <div className="flex flex-wrap gap-2">
              {banks.map((b) => (
                <span
                  key={b.id}
                  className={`text-xs px-2 py-1 rounded ${
                    b.status === "available" ? "bg-green-50 text-green-700" : "bg-gray-100 text-gray-500"
                  }`}
                >
                  {b.name}
                </span>
              ))}
            </div>
          </div>
          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="block w-full text-sm file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:bg-primary/10 file:text-primary hover:file:bg-primary/20"
          />
          <button
            onClick={handleImport}
            disabled={!file || loading}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
            {loading ? "Reconciling..." : "Import & Reconcile"}
          </button>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 mb-6 rounded-lg bg-destructive/10 text-destructive">
          <AlertCircle className="h-4 w-4" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {result && (
        <div className="border rounded-lg p-6 bg-card">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <h2 className="font-medium">Reconciliation Complete</h2>
          </div>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="p-3 rounded bg-muted">
              <div className="text-sm text-muted-foreground">Matched</div>
              <div className="font-medium">{result.matched?.length || 0}</div>
            </div>
            <div className="p-3 rounded bg-muted">
              <div className="text-sm text-muted-foreground">Unmatched Bank</div>
              <div className="font-medium">{result.unmatched_bank_entries?.length || 0}</div>
            </div>
            <div className="p-3 rounded bg-muted">
              <div className="text-sm text-muted-foreground">Reconciliation Rate</div>
              <div className="font-medium">{result.reconciliation_rate ? `${result.reconciliation_rate}%` : "—"}</div>
            </div>
            <div className="p-3 rounded bg-muted">
              <div className="text-sm text-muted-foreground">Auto-Created</div>
              <div className="font-medium">{result.transactions_created || 0}</div>
            </div>
          </div>
          {result.recurring_patterns?.length > 0 && (
            <div className="mt-4">
              <h3 className="text-sm font-medium mb-2">Recurring Patterns Detected</h3>
              <div className="space-y-1">
                {result.recurring_patterns.map((p: any, i: number) => (
                  <div key={i} className="text-sm p-2 rounded bg-muted">
                    {p.description} — {p.frequency}, avg ₦{p.avg_amount?.toLocaleString()}
                  </div>
                ))}
              </div>
            </div>
          )}
          {result.summary && <p className="mt-4 text-sm text-muted-foreground">{result.summary}</p>}
        </div>
      )}
    </div>
  );
}
