"use client";

import { useState, useEffect } from "react";
import { useOrg } from "@/lib/org-context";
import { getSupplierScores, getSupplierReport } from "@/lib/api";
import { Shield, TrendingUp, AlertTriangle, Loader2, Brain } from "lucide-react";

interface SupplierScore {
  supplier_id: string;
  supplier_name: string;
  reliability_score: number;
  transaction_count: number;
  price_stability?: string;
  delivery_consistency?: string;
  risk_flags?: string[];
  total_spend?: number;
}

export default function SupplierIntelligencePage() {
  const { orgId } = useOrg();
  const [scores, setScores] = useState<SupplierScore[]>([]);
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [reportLoading, setReportLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!orgId) return;
    setLoading(true);
    getSupplierScores(orgId)
      .then(setScores)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [orgId]);

  const generateReport = async () => {
    if (!orgId) return;
    setReportLoading(true);
    try {
      const data = await getSupplierReport(orgId);
      setReport(data);
      // Update scores from report if available
      if (data.supplier_scores) setScores(data.supplier_scores);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setReportLoading(false);
    }
  };

  const scoreColor = (score: number) => {
    if (score >= 80) return "text-green-600 bg-green-50";
    if (score >= 60) return "text-yellow-600 bg-yellow-50";
    return "text-red-600 bg-red-50";
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Shield className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-semibold">Supplier Intelligence</h1>
        </div>
        <button
          onClick={generateReport}
          disabled={reportLoading}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
        >
          {reportLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Brain className="h-4 w-4" />}
          {reportLoading ? "Analysing..." : "AI Analysis"}
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 mb-6 rounded-lg bg-destructive/10 text-destructive">
          <AlertTriangle className="h-4 w-4" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {/* Supplier Scores Table */}
      <div className="border rounded-lg bg-card mb-6">
        <div className="p-4 border-b">
          <h2 className="font-medium">Supplier Reliability Scores</h2>
        </div>
        {loading ? (
          <div className="flex items-center justify-center p-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : scores.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            No suppliers found. Add suppliers via the Suppliers page first.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="text-left p-3">Supplier</th>
                  <th className="text-center p-3">Score</th>
                  <th className="text-center p-3">Transactions</th>
                  <th className="text-center p-3">Price</th>
                  <th className="text-center p-3">Delivery</th>
                </tr>
              </thead>
              <tbody>
                {scores.map((s) => (
                  <tr key={s.supplier_id} className="border-b last:border-0">
                    <td className="p-3 font-medium">{s.supplier_name}</td>
                    <td className="p-3 text-center">
                      <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${scoreColor(s.reliability_score)}`}>
                        {s.reliability_score}
                      </span>
                    </td>
                    <td className="p-3 text-center text-muted-foreground">{s.transaction_count}</td>
                    <td className="p-3 text-center text-muted-foreground">{s.price_stability || "—"}</td>
                    <td className="p-3 text-center text-muted-foreground">{s.delivery_consistency || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* AI Report */}
      {report && (
        <>
          {report.single_source_risks?.length > 0 && (
            <div className="border rounded-lg p-4 mb-6 bg-card">
              <h2 className="font-medium mb-3 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-yellow-600" />
                Single-Source Risks
              </h2>
              <div className="space-y-2">
                {report.single_source_risks.map((r: any, i: number) => (
                  <div key={i} className="p-3 rounded bg-yellow-50 text-sm">
                    <span className="font-medium">{r.item_name}</span> — only from {r.current_supplier}.{" "}
                    <span className="text-muted-foreground">{r.recommendation}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {report.recommendations?.length > 0 && (
            <div className="border rounded-lg p-4 bg-card">
              <h2 className="font-medium mb-3 flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-primary" />
                Recommendations
              </h2>
              <ul className="space-y-2">
                {report.recommendations.map((rec: string, i: number) => (
                  <li key={i} className="text-sm p-2 rounded bg-muted">{rec}</li>
                ))}
              </ul>
              {report.summary && (
                <p className="mt-4 text-sm text-muted-foreground">{report.summary}</p>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
