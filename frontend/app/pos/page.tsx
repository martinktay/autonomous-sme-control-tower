/**
 * @file POS Connector page (/pos) — Import POS system exports and view supported systems.
 * Parses CSV/Excel POS data via AI and auto-creates revenue transactions.
 */
"use client";

import { useState, useEffect } from "react";
import { useOrg } from "@/lib/org-context";
import { importPosData, getSupportedPosSystems } from "@/lib/api";
import { CreditCard, Upload, CheckCircle, AlertCircle, Loader2 } from "lucide-react";

export default function PosConnectorPage() {
  const { orgId } = useOrg();
  const [file, setFile] = useState<File | null>(null);
  const [posSystem, setPosSystem] = useState("generic_csv");
  const [systems, setSystems] = useState<any[]>([]);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getSupportedPosSystems()
      .then((data) => setSystems(data.supported_systems || []))
      .catch(() => {});
  }, []);

  const handleImport = async () => {
    if (!file || !orgId) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await importPosData(orgId, file, posSystem);
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
        <CreditCard className="h-6 w-6 text-primary" />
        <h1 className="text-2xl font-semibold">POS Connector</h1>
      </div>
      <p className="text-muted-foreground mb-6">
        Import sales data from your POS system. Upload a CSV or Excel export and our AI extracts transactions automatically.
      </p>

      <div className="border rounded-lg p-6 mb-6 bg-card">
        <h2 className="font-medium mb-4">Import POS Data</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm mb-1 text-muted-foreground">POS System</label>
            <select
              value={posSystem}
              onChange={(e) => setPosSystem(e.target.value)}
              className="w-full border rounded-md px-3 py-2 text-sm bg-background"
            >
              {systems.map((s) => (
                <option key={s.id} value={s.id} disabled={s.status === "coming_soon"}>
                  {s.name} {s.status === "coming_soon" ? "(Coming Soon)" : ""}
                </option>
              ))}
            </select>
          </div>
          <input
            type="file"
            accept=".csv,.xlsx,.xls,.txt"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="block w-full text-sm file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:bg-primary/10 file:text-primary hover:file:bg-primary/20"
          />
          <button
            onClick={handleImport}
            disabled={!file || loading}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
            {loading ? "Processing..." : "Import"}
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
            <h2 className="font-medium">Import Complete</h2>
          </div>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="p-3 rounded bg-muted">
              <div className="text-sm text-muted-foreground">POS Detected</div>
              <div className="font-medium">{result.pos_system_detected || "—"}</div>
            </div>
            <div className="p-3 rounded bg-muted">
              <div className="text-sm text-muted-foreground">Transactions</div>
              <div className="font-medium">{result.transactions?.length || 0}</div>
            </div>
            <div className="p-3 rounded bg-muted">
              <div className="text-sm text-muted-foreground">Created</div>
              <div className="font-medium">{result.transactions_created || 0}</div>
            </div>
          </div>
          {result.summary && <p className="text-sm text-muted-foreground">{result.summary}</p>}
        </div>
      )}
    </div>
  );
}
