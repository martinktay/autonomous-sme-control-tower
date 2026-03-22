"use client";

import { useState } from "react";
import { useOrg } from "@/lib/org-context";
import { uploadSyncFile, getSyncStatus } from "@/lib/api";
import { HardDrive, Upload, CheckCircle, AlertCircle, Loader2 } from "lucide-react";

export default function DesktopSyncPage() {
  const { orgId } = useOrg();
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [syncStatus, setSyncStatus] = useState<any>(null);

  const handleUpload = async () => {
    if (!file || !orgId) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await uploadSyncFile(orgId, file);
      setResult(data);
    } catch (e: any) {
      setError(e.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const checkStatus = async () => {
    if (!orgId) return;
    try {
      const data = await getSyncStatus(orgId);
      setSyncStatus(data);
    } catch (e: any) {
      setError(e.message);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <div className="flex items-center gap-3 mb-6">
        <HardDrive className="h-6 w-6 text-primary" />
        <h1 className="text-2xl font-semibold">Desktop Sync</h1>
      </div>
      <p className="text-muted-foreground mb-6">
        Upload POS export files or sales data from your desktop. Our AI extracts transactions automatically.
      </p>

      {/* Upload Section */}
      <div className="border rounded-lg p-6 mb-6 bg-card">
        <h2 className="font-medium mb-4">Upload POS Export</h2>
        <div className="space-y-4">
          <input
            type="file"
            accept=".csv,.xlsx,.xls,.txt"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="block w-full text-sm file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:bg-primary/10 file:text-primary hover:file:bg-primary/20"
          />
          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
            {loading ? "Processing..." : "Upload & Extract"}
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
        <div className="border rounded-lg p-6 mb-6 bg-card">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <h2 className="font-medium">Extraction Complete</h2>
          </div>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="p-3 rounded bg-muted">
              <div className="text-sm text-muted-foreground">File Type</div>
              <div className="font-medium">{result.file_type_detected || "—"}</div>
            </div>
            <div className="p-3 rounded bg-muted">
              <div className="text-sm text-muted-foreground">Records Found</div>
              <div className="font-medium">{result.records_found || 0}</div>
            </div>
            <div className="p-3 rounded bg-muted">
              <div className="text-sm text-muted-foreground">Transactions Created</div>
              <div className="font-medium">{result.transactions_created || 0}</div>
            </div>
            <div className="p-3 rounded bg-muted">
              <div className="text-sm text-muted-foreground">Unparsed Rows</div>
              <div className="font-medium">{result.unparsed_rows?.length || 0}</div>
            </div>
          </div>
          {result.summary && <p className="text-sm text-muted-foreground">{result.summary}</p>}
        </div>
      )}

      {/* Sync Status */}
      <div className="border rounded-lg p-6 bg-card">
        <h2 className="font-medium mb-4">Sync Agent Status</h2>
        <button
          onClick={checkStatus}
          className="px-4 py-2 text-sm border rounded-md hover:bg-accent mb-4"
        >
          Check Status
        </button>
        {syncStatus && (
          <div className="p-4 rounded bg-muted text-sm">
            <p>{syncStatus.message}</p>
            <p className="mt-2 text-muted-foreground">
              Sync enabled: {syncStatus.sync_enabled ? "Yes" : "No"}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
