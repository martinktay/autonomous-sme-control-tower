"use client";

import { useState, useEffect } from "react";
import { useOrg } from "@/lib/org-context";
import { getBranchBenchmarks, getBranchOptimisation } from "@/lib/api";
import { GitBranch, AlertTriangle, Loader2, Brain, ArrowRightLeft } from "lucide-react";

export default function BranchOptimisationPage() {
  const { orgId } = useOrg();
  const [benchmarks, setBenchmarks] = useState<any>(null);
  const [optimisation, setOptimisation] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [optLoading, setOptLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!orgId) return;
    setLoading(true);
    getBranchBenchmarks(orgId)
      .then(setBenchmarks)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [orgId]);

  const runOptimisation = async () => {
    if (!orgId) return;
    setOptLoading(true);
    try {
      const data = await getBranchOptimisation(orgId);
      setOptimisation(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setOptLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <GitBranch className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-semibold">Cross-Branch Optimisation</h1>
        </div>
        <button
          onClick={runOptimisation}
          disabled={optLoading}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
        >
          {optLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Brain className="h-4 w-4" />}
          {optLoading ? "Optimising..." : "AI Optimise"}
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 mb-6 rounded-lg bg-destructive/10 text-destructive">
          <AlertTriangle className="h-4 w-4" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {/* Branch List */}
      {loading ? (
        <div className="flex items-center justify-center p-8">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : benchmarks && (
        <div className="border rounded-lg bg-card mb-6">
          <div className="p-4 border-b">
            <h2 className="font-medium">Branches ({benchmarks.total_branches || 0})</h2>
          </div>
          {benchmarks.branches?.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              No branches found. Add branches via the onboarding flow or business settings.
            </div>
          ) : (
            <div className="divide-y">
              {benchmarks.branches?.map((b: any) => (
                <div key={b.branch_id} className="p-4 flex items-center justify-between">
                  <div>
                    <div className="font-medium">{b.branch_name}</div>
                    {b.address && <div className="text-sm text-muted-foreground">{b.address}</div>}
                  </div>
                  <span className="text-xs px-2 py-1 rounded bg-green-50 text-green-700">{b.status}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Optimisation Results */}
      {optimisation && (
        <>
          {optimisation.message ? (
            <div className="p-4 rounded-lg bg-muted text-sm">{optimisation.message}</div>
          ) : (
            <>
              {optimisation.transfer_recommendations?.length > 0 && (
                <div className="border rounded-lg bg-card mb-6">
                  <div className="p-4 border-b">
                    <h2 className="font-medium flex items-center gap-2">
                      <ArrowRightLeft className="h-4 w-4" />
                      Stock Transfer Recommendations
                    </h2>
                  </div>
                  <div className="divide-y">
                    {optimisation.transfer_recommendations.map((t: any, i: number) => (
                      <div key={i} className="p-4">
                        <div className="font-medium text-sm">{t.item_name}</div>
                        <div className="text-sm text-muted-foreground mt-1">
                          Move {t.quantity} units from {t.from_branch} → {t.to_branch}
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">{t.reason}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {optimisation.branch_benchmarks?.length > 0 && (
                <div className="border rounded-lg bg-card mb-6">
                  <div className="p-4 border-b">
                    <h2 className="font-medium">Branch Performance</h2>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b bg-muted/50">
                          <th className="text-left p-3">Branch</th>
                          <th className="text-center p-3">Revenue</th>
                          <th className="text-center p-3">Items</th>
                          <th className="text-center p-3">Low Stock</th>
                          <th className="text-center p-3">Performance</th>
                        </tr>
                      </thead>
                      <tbody>
                        {optimisation.branch_benchmarks.map((b: any, i: number) => (
                          <tr key={i} className="border-b last:border-0">
                            <td className="p-3 font-medium">{b.branch_name}</td>
                            <td className="p-3 text-center">₦{b.total_revenue?.toLocaleString()}</td>
                            <td className="p-3 text-center">{b.total_items}</td>
                            <td className="p-3 text-center">{b.low_stock_count}</td>
                            <td className="p-3 text-center">
                              <span className={`text-xs px-2 py-1 rounded ${
                                b.performance === "strong" ? "bg-green-50 text-green-700" :
                                b.performance === "average" ? "bg-yellow-50 text-yellow-700" :
                                "bg-red-50 text-red-700"
                              }`}>
                                {b.performance}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {optimisation.recommendations?.length > 0 && (
                <div className="border rounded-lg p-4 mb-6 bg-card">
                  <h2 className="font-medium mb-3">Recommendations</h2>
                  <ul className="space-y-2">
                    {optimisation.recommendations.map((rec: string, i: number) => (
                      <li key={i} className="text-sm p-2 rounded bg-muted">{rec}</li>
                    ))}
                  </ul>
                </div>
              )}

              {optimisation.summary && (
                <div className="p-4 rounded-lg bg-primary/5 text-sm">{optimisation.summary}</div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}
