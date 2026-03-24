/**
 * @file Finance page (/finance) — Financial dashboard with P&L, cashflow, analytics, and document management.
 * Includes review queue, CSV/XLSX export, and AI-powered financial insights.
 */
"use client";

import { useState, useEffect, useCallback } from "react";
import CashflowChart from "@/components/CashflowChart";
import PnlSummary from "@/components/PnlSummary";
import FinanceInsightsPanel from "@/components/FinanceInsightsPanel";
import FinanceAnalytics from "@/components/FinanceAnalytics";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { getFinanceInsights } from "@/lib/api";
import { useOrg } from "@/lib/org-context";
import {
  Upload,
  ClipboardList,
  Download,
  RefreshCw,
  Loader2,
} from "lucide-react";

export default function FinanceDashboardPage() {
  const { orgId } = useOrg();
  const [insights, setInsights] = useState<any>(null);
  const [insightsLoading, setInsightsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [lastRefresh, setLastRefresh] = useState("");

  const fetchInsights = useCallback(
    async (isRefresh = false) => {
      if (isRefresh) setRefreshing(true);
      else setInsightsLoading(true);
      try {
        const res = await getFinanceInsights(orgId);
        setInsights(res.insights || null);
        setLastRefresh(new Date().toLocaleTimeString());
      } catch {
        setInsights(null);
      } finally {
        setInsightsLoading(false);
        setRefreshing(false);
      }
    },
    [orgId]
  );

  useEffect(() => {
    fetchInsights();
  }, [fetchInsights]);

  const handleRefreshAll = () => {
    fetchInsights(true);
    setRefreshKey((k) => k + 1);
  };

  return (
    <div className="container mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold mb-1">Finance Dashboard</h1>
          <p className="text-muted-foreground">
            Your money at a glance — see where it comes from, where it goes, and how much tax you owe. No accounting knowledge needed.
            {lastRefresh && (
              <span className="ml-2 text-xs">Updated {lastRefresh}</span>
            )}
          </p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <Link href="/finance/upload">
            <Button variant="outline" size="sm">
              <Upload className="h-4 w-4 mr-1" /> Upload
            </Button>
          </Link>
          <Link href="/finance/review">
            <Button variant="outline" size="sm">
              <ClipboardList className="h-4 w-4 mr-1" /> Review
            </Button>
          </Link>
          <Link href="/finance/export">
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-1" /> Export
            </Button>
          </Link>
          <Button variant="outline" size="sm" onClick={handleRefreshAll} disabled={refreshing}>
            {refreshing ? (
              <Loader2 className="h-4 w-4 mr-1 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4 mr-1" />
            )}
            Refresh All
          </Button>
        </div>
      </div>

      {/* AI Financial Insights */}
      <FinanceInsightsPanel
        insights={insights}
        loading={insightsLoading}
        onRefresh={() => fetchInsights(true)}
        refreshing={refreshing}
      />

      {/* Analytics Charts — KPIs, pie charts, bar charts, vendor table */}
      <div className="grid gap-6">
        <FinanceAnalytics refreshKey={refreshKey} />
      </div>

      {/* Cashflow & P&L detail */}
      <div className="grid gap-6 lg:grid-cols-2">
        <CashflowChart />
        <PnlSummary />
      </div>
    </div>
  );
}
