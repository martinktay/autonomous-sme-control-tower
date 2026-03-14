/**
 * @file Dashboard page (/dashboard) — Primary business overview screen.
 * Fetches NSI score, risks, actions, and AI insights for the active org.
 * Auto-refreshes every 30 s and supports manual refresh / closed-loop trigger.
 */
"use client";

import { useState, useEffect, useCallback } from "react";
import NSICard from "@/components/NsiCard";
import RiskPanel from "@/components/RiskPanel";
import ActionLog from "@/components/ActionLog";
import InsightsPanel from "@/components/InsightsPanel";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { apiClient } from "@/lib/api";
import { useOrg } from "@/lib/org-context";
import { RefreshCw, Play, HelpCircle, WifiOff } from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const { orgId, orgName } = useOrg();
  const [nsiData, setNsiData] = useState<any>(null);
  const [actions, setActions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [runningLoop, setRunningLoop] = useState(false);
  const [insights, setInsights] = useState<any>(null);
  const [insightsLoading, setInsightsLoading] = useState(false);

  // Fetch NSI + actions in parallel; show error only if both fail
  const fetchDashboardData = useCallback(async (silent = false) => {
    try {
      if (!silent) setLoading(true);
      setRefreshing(true);
      setError(null);

      const [nsiResponse, actionsResponse] = await Promise.allSettled([
        apiClient.getNSI(orgId),
        apiClient.getActions(orgId),
      ]);

      if (nsiResponse.status === "fulfilled") {
        setNsiData(nsiResponse.value.nsi);
      }
      if (actionsResponse.status === "fulfilled") {
        setActions(actionsResponse.value.actions || []);
      }

      // If both failed, show error
      if (
        nsiResponse.status === "rejected" &&
        actionsResponse.status === "rejected"
      ) {
        setError(
          "Could not connect to the server. Make sure the backend is running on port 8000."
        );
      }
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [orgId]);

  // Trigger the full ingest → diagnose → act orchestration loop
  const runClosedLoop = async () => {
    try {
      setRunningLoop(true);
      await apiClient.runClosedLoop(orgId);
      await fetchDashboardData();
    } catch (err: any) {
      setError(err.message || "Failed to run analysis");
    } finally {
      setRunningLoop(false);
    }
  };

  // On-demand AI insights generation with error fallback
  const fetchInsights = async () => {
    try {
      setInsightsLoading(true);
      const res = await apiClient.getBusinessInsights(orgId);
      setInsights(res.insights);
    } catch (err: any) {
      // Show error in insights panel via a fallback object
      setInsights({
        summary: err.message || "Could not generate insights right now. Please try again later.",
        highlights: [],
        next_steps: ["Make sure the backend is running and connected to AWS Bedrock."],
        confidence: "low",
      });
    } finally {
      setInsightsLoading(false);
    }
  };

  // Initial fetch + 30 s polling; reset insights when org changes
  useEffect(() => {
    setInsights(null);
    fetchDashboardData();
    const interval = setInterval(() => fetchDashboardData(true), 30000);
    return () => clearInterval(interval);
  }, [fetchDashboardData]);

  const nsi = nsiData?.nsi_score ?? nsiData?.nova_stability_index ?? null;
  const confidence = nsiData?.confidence || "medium";
  const timestamp = nsiData?.timestamp;
  const risks = nsiData?.top_risks || [];

  return (
    <div className="min-h-screen bg-background p-4 sm:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              {orgName}
            </h1>
            <p className="text-muted-foreground mt-1">
              Your business health at a glance. The score updates each time you
              upload data or run an analysis.
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => fetchDashboardData(false)}
              disabled={refreshing}
            >
              <RefreshCw
                className={`h-4 w-4 mr-2 ${refreshing ? "animate-spin" : ""}`}
              />
              Refresh
            </Button>
            <Button
              size="sm"
              onClick={runClosedLoop}
              disabled={runningLoop || refreshing}
            >
              <Play
                className={`h-4 w-4 mr-2 ${runningLoop ? "animate-pulse" : ""}`}
              />
              Run Analysis
            </Button>
          </div>
        </div>

        {/* Connection error banner */}
        {error && !loading && (
          <Card className="border-destructive/50 bg-destructive/5">
            <CardContent className="py-4">
              <div className="flex items-center gap-3">
                <WifiOff className="h-5 w-5 text-destructive shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-destructive">
                    {error}
                  </p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Start the backend with: uvicorn app.main:app --reload --port
                    8000
                  </p>
                </div>
                <Button variant="outline" size="sm" onClick={() => fetchDashboardData(false)}>
                  Retry
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* NSI Card */}
        <NSICard
          nsi={nsi}
          confidence={confidence}
          timestamp={timestamp}
          loading={loading}
        />

        {/* Sub-indices */}
        {nsiData && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <SubIndexCard
              label="Cash Flow"
              value={nsiData.liquidity_index}
              hint="How well you can pay your bills on time"
            />
            <SubIndexCard
              label="Revenue Stability"
              value={nsiData.revenue_stability_index}
              hint="How consistent your income has been"
            />
            <SubIndexCard
              label="Operations Speed"
              value={nsiData.operational_latency_index}
              hint="How quickly your business processes run"
            />
            <SubIndexCard
              label="Vendor Risk"
              value={nsiData.vendor_risk_index}
              hint="How reliable your suppliers are"
            />
          </div>
        )}

        {/* No data state — only show when not loading and no error */}
        {!loading && !error && !nsiData && (
          <Card>
            <CardContent className="py-10 text-center space-y-3">
              <HelpCircle className="h-10 w-10 mx-auto text-muted-foreground" />
              <h3 className="font-semibold">No data yet</h3>
              <p className="text-sm text-muted-foreground max-w-md mx-auto">
                Upload your first invoice to get started. Once you have data,
                run an analysis to see your business health score.
              </p>
              <div className="flex justify-center gap-2 pt-2">
                <Link href="/upload">
                  <Button>Upload Invoice</Button>
                </Link>
                <Link href="/help">
                  <Button variant="outline">How It Works</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        )}

        {/* AI Business Insights */}
        <InsightsPanel
          insights={insights}
          loading={loading}
          onGenerate={fetchInsights}
          generating={insightsLoading}
        />

        {/* Risks and Actions — pass loading=false once fetch completes */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <RiskPanel risks={risks} loading={loading} />
          <ActionLog actions={actions} loading={loading} />
        </div>
      </div>
    </div>
  );
}

/** SubIndexCard — Small KPI card for an individual NSI sub-index (e.g. Cash Flow). */
function SubIndexCard({
  label,
  value,
  hint,
}: {
  label: string;
  value?: number;
  hint: string;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription>{label}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">
          {value != null ? value.toFixed(1) : "--"}
        </div>
        <p className="text-xs text-muted-foreground mt-1">{hint}</p>
      </CardContent>
    </Card>
  );
}
