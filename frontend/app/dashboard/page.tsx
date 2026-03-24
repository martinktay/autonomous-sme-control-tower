/**
 * @file Dashboard page (/dashboard) — Primary business overview screen.
 * Fetches BSI score, risks, actions, and AI insights for the active org.
 * Auto-refreshes every 30 s and supports manual refresh / closed-loop trigger.
 */
"use client";

import { useState, useEffect, useCallback } from "react";
import BSICard from "@/components/BsiCard";
import RiskPanel from "@/components/RiskPanel";
import ActionLog from "@/components/ActionLog";
import InsightsPanel from "@/components/InsightsPanel";
import InventoryTable from "@/components/InventoryTable";
import SupplierCard from "@/components/SupplierCard";
import StockAlertBadge from "@/components/StockAlertBadge";
import SalesTrendChart from "@/components/SalesTrendChart";
import TopProductsTable from "@/components/TopProductsTable";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
} from "@/components/ui/card";
import { apiClient } from "@/lib/api";
import { useOrg } from "@/lib/org-context";
import { RefreshCw, Play, HelpCircle, WifiOff, Package, Users } from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const { orgId, orgName } = useOrg();
  const [bsiData, setBsiData] = useState<any>(null);
  const [actions, setActions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [runningLoop, setRunningLoop] = useState(false);
  const [insights, setInsights] = useState<any>(null);
  const [insightsLoading, setInsightsLoading] = useState(false);
  const [inventory, setInventory] = useState<any[]>([]);
  const [stockAlerts, setStockAlerts] = useState<any[]>([]);
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [recentTransactions, setRecentTransactions] = useState<any[]>([]);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Fetch BSI + actions in parallel; show error only if both fail
  const fetchDashboardData = useCallback(async (silent = false) => {
    try {
      if (!silent) setLoading(true);
      setRefreshing(true);
      setError(null);

      const [bsiResponse, actionsResponse] = await Promise.allSettled([
        apiClient.getNSI(orgId),
        apiClient.getActions(orgId),
      ]);

      if (bsiResponse.status === "fulfilled") {
        setBsiData(bsiResponse.value.bsi);
      }
      if (actionsResponse.status === "fulfilled") {
        setActions(actionsResponse.value.actions || []);
      }

      // If both failed, show error
      if (
        bsiResponse.status === "rejected" &&
        actionsResponse.status === "rejected"
      ) {
        setError(
          "Could not connect to the server. Make sure the backend is running on port 8000."
        );
      }

      // Fetch inventory, supplier, and transaction data (best-effort, don't block dashboard)
      Promise.allSettled([
        apiClient.getInventory(orgId).then((r: any) => r.json ? r.json() : r),
        apiClient.getStockAlerts(orgId).then((r: any) => r.json ? r.json() : r),
        apiClient.getCounterparties(orgId).then((r: any) => r.json ? r.json() : r),
        apiClient.getTransactions(orgId).then((r: any) => r.json ? r.json() : r),
      ]).then(([invRes, alertRes, suppRes, txnRes]) => {
        if (invRes.status === "fulfilled") setInventory(Array.isArray(invRes.value) ? invRes.value : []);
        if (alertRes.status === "fulfilled") setStockAlerts(Array.isArray(alertRes.value) ? alertRes.value : []);
        if (suppRes.status === "fulfilled") setSuppliers(Array.isArray(suppRes.value) ? suppRes.value : []);
        if (txnRes.status === "fulfilled") setRecentTransactions(Array.isArray(txnRes.value) ? txnRes.value : []);
      });
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
      setRefreshing(false);
      setLastUpdated(new Date());
    }
  }, [orgId]);

  // Trigger the full ingest → diagnose → act orchestration loop
  const runClosedLoop = async () => {
    try {
      setRunningLoop(true);
      setError(null);
      const result = await apiClient.runClosedLoop(orgId);
      if (result.status === "no_data") {
        setError(result.message || "No data yet. Upload invoices or documents first, then run the analysis.");
      } else {
        await fetchDashboardData();
      }
    } catch (err: any) {
      const msg = err.message || "Failed to run analysis";
      if (msg.includes("No signals") || msg.includes("no_data")) {
        setError("No data yet. Upload invoices or documents first, then run the analysis.");
      } else {
        setError(msg);
      }
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

  const bsi = bsiData?.bsi_score ?? bsiData?.business_stability_index ?? null;
  const confidence = bsiData?.confidence || "medium";
  const timestamp = bsiData?.timestamp;
  const risks = bsiData?.top_risks || bsiData?.sub_indices?.top_risks || [];

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
          <div className="flex items-center gap-2">
            {lastUpdated && (
              <span className="text-xs text-muted-foreground hidden sm:inline">
                Updated {lastUpdated.toLocaleTimeString()}
              </span>
            )}
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
                  {error.toLowerCase().includes("connect") && (
                    <p className="text-xs text-muted-foreground mt-0.5">
                      Start the backend with: uvicorn app.main:app --reload --port 8000
                    </p>
                  )}
                </div>
                <Button variant="outline" size="sm" onClick={() => { setError(null); fetchDashboardData(false); }}>
                  Retry
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* BSI Card */}
        <BSICard
          bsi={bsi}
          confidence={confidence}
          timestamp={timestamp}
          loading={loading}
        />

        {/* Sub-indices */}
        {bsiData && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <SubIndexCard
              label="Cash Flow"
              value={bsiData.liquidity_index}
              hint="Can you pay your bills on time? This measures the balance between money coming in and money going out. A low score means you may struggle to cover expenses — consider chasing overdue invoices or delaying non-urgent purchases."
            />
            <SubIndexCard
              label="Revenue Stability"
              value={bsiData.revenue_stability_index}
              hint="Is your income steady or unpredictable? This tracks how consistent your revenue has been. A high score means reliable income; a low score means your earnings vary a lot — which makes planning harder."
            />
            <SubIndexCard
              label="Operations Speed"
              value={bsiData.operational_latency_index}
              hint="How fast do things get done in your business? This measures delays in processing invoices, fulfilling orders, and completing tasks. A low score means bottlenecks are slowing you down — look for incomplete or missing data."
            />
            <SubIndexCard
              label="Vendor Risk"
              value={bsiData.vendor_risk_index}
              hint="How dependable are your suppliers? This checks if you rely too heavily on one vendor, have late deliveries, or missing documentation. A low score means your supply chain is fragile — consider diversifying your suppliers."
            />
          </div>
        )}

        {/* No data state — only show when not loading and no error */}
        {!loading && !error && !bsiData && (
          <Card>
            <CardContent className="py-10 text-center space-y-3">
              <HelpCircle className="h-10 w-10 mx-auto text-muted-foreground" />
              <h3 className="font-semibold">Welcome to your Control Tower</h3>
              <p className="text-sm text-muted-foreground max-w-md mx-auto">
                Upload an invoice, receipt, or spreadsheet to get started.
                The AI will calculate your business health score, spot risks,
                and suggest improvements — all in plain language.
              </p>
              <div className="flex flex-wrap justify-center gap-2 pt-2">
                <Link href="/upload">
                  <Button>Upload Invoice</Button>
                </Link>
                <Link href="/finance/upload">
                  <Button variant="outline">Import Spreadsheet</Button>
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

        {/* Inventory & Supplier Quick View (shows when data exists) */}
        {(inventory.length > 0 || stockAlerts.length > 0 || suppliers.length > 0) && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Stock overview */}
            {(inventory.length > 0 || stockAlerts.length > 0) && (
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-2">
                    <Package className="h-4 w-4 text-primary" />
                    <span className="font-medium text-sm">Stock Overview</span>
                    {stockAlerts.length > 0 && (
                      <span className="ml-auto text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">
                        {stockAlerts.length} alert{stockAlerts.length !== 1 ? "s" : ""}
                      </span>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  {stockAlerts.length > 0 && (
                    <div className="space-y-1 mb-3">
                      {stockAlerts.slice(0, 3).map((alert: any, i: number) => (
                        <div key={i} className="flex items-center gap-2 text-xs text-red-600">
                          <span className="w-1.5 h-1.5 rounded-full bg-red-500 shrink-0" />
                          {alert.item_name || alert.message || "Low stock alert"}
                        </div>
                      ))}
                    </div>
                  )}
                  <p className="text-xs text-muted-foreground">
                    {inventory.length} item{inventory.length !== 1 ? "s" : ""} tracked.{" "}
                    <Link href="/inventory" className="text-primary hover:underline">View all →</Link>
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Supplier overview */}
            {suppliers.length > 0 && (
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-primary" />
                    <span className="font-medium text-sm">Suppliers & Customers</span>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {suppliers.slice(0, 4).map((s: any) => (
                      <div key={s.counterparty_id || s.name} className="flex items-center justify-between text-sm">
                        <span className="truncate">{s.name}</span>
                        <span className="text-xs text-muted-foreground capitalize">{s.counterparty_type || "supplier"}</span>
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    {suppliers.length} total.{" "}
                    <Link href="/suppliers" className="text-primary hover:underline">View all →</Link>
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Risks and Actions — pass loading=false once fetch completes */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <RiskPanel risks={risks} loading={loading} />
          <ActionLog actions={actions} loading={loading} />
        </div>

        {/* Sales Trend & Top Products (shows when data exists) */}
        {(recentTransactions.length > 0 || inventory.length > 0) && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {recentTransactions.length > 0 && (
              <Card>
                <CardHeader className="pb-2">
                  <span className="font-medium text-sm">Sales Trend (14 days)</span>
                  <CardDescription>Daily revenue from your transactions</CardDescription>
                </CardHeader>
                <CardContent>
                  <SalesTrendChart transactions={recentTransactions} />
                </CardContent>
              </Card>
            )}
            {inventory.length > 0 && (
              <Card>
                <CardHeader className="pb-2">
                  <span className="font-medium text-sm">Top Products</span>
                  <CardDescription>Best sellers by quantity sold</CardDescription>
                </CardHeader>
                <CardContent>
                  <TopProductsTable items={inventory} />
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/** SubIndexCard — Small KPI card for an individual BSI sub-index (e.g. Cash Flow). */
function SubIndexCard({
  label,
  value,
  hint,
}: {
  label: string;
  value?: number;
  hint: string;
}) {
  const getColor = (v: number) => {
    if (v >= 70) return "text-green-600";
    if (v >= 40) return "text-yellow-600";
    return "text-red-600";
  };

  const getLabel = (v: number) => {
    if (v >= 70) return "Good";
    if (v >= 40) return "Needs attention";
    return "Act now";
  };

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription className="font-medium">{label}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline gap-2">
          <span className={`text-2xl font-bold ${value != null ? getColor(value) : ""}`}>
            {value != null ? value.toFixed(1) : "--"}
          </span>
          {value != null && (
            <span className={`text-xs ${getColor(value)}`}>{getLabel(value)}</span>
          )}
        </div>
        <p className="text-xs text-muted-foreground mt-2 leading-relaxed">{hint}</p>
      </CardContent>
    </Card>
  );
}
