/**
 * FinanceAnalytics — Fetches and renders financial KPIs, pie charts,
 * bar charts (monthly trend), vendor expense table, and tax/VAT breakdowns.
 * Auto-refreshes when orgId or refreshKey changes.
 */
"use client";

import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import PieChart from "@/components/charts/PieChart";
import BarChart from "@/components/charts/BarChart";
import { getFinanceAnalytics } from "@/lib/api";
import { useOrg } from "@/lib/org-context";
import {
  Loader2,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Receipt,
  Minus,
} from "lucide-react";

interface AnalyticsData {
  expense_by_vendor: { name: string; value: number }[];
  revenue_by_source: { name: string; value: number }[];
  category_breakdown: { name: string; count: number; total: number }[];
  currency_breakdown: { currency: string; total: number }[];
  vat_breakdown: { collected: number; paid: number; net_liability: number };
  tax_breakdown: { name: string; value: number }[];
  tax_summary: { total_tax_burden: number; [key: string]: number };
  monthly_trend: { period: string; revenue: number; expenses: number; net: number }[];
  totals: { revenue: number; expenses: number; net_profit: number; document_count: number; total_tax_burden: number };
}

interface FinanceAnalyticsProps {
  refreshKey?: number;
}

const fmt = (v: number) =>
  v.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export default function FinanceAnalytics({ refreshKey }: FinanceAnalyticsProps) {
  const { orgId } = useOrg();
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getFinanceAnalytics(orgId);
      setData(res.analytics || null);
    } catch {
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [orgId]);

  useEffect(() => {
    fetchData();
  }, [fetchData, refreshKey]);

  if (loading) {
    return (
      <Card className="col-span-full">
        <CardContent className="flex items-center gap-2 py-8 text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span className="text-sm">Loading analytics…</span>
        </CardContent>
      </Card>
    );
  }

  if (!data || data.totals.document_count === 0) {
    return (
      <Card className="col-span-full">
        <CardContent className="text-center py-8">
          <p className="text-sm text-muted-foreground">
            No financial data yet. Upload invoices, receipts, or spreadsheets to see charts and analytics.
          </p>
        </CardContent>
      </Card>
    );
  }

  const { totals, vat_breakdown: vat } = data;
  const margin = totals.revenue > 0 ? (totals.net_profit / totals.revenue) * 100 : 0;

  return (
    <>
      {/* KPI Row */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 col-span-full">
        <Card>
          <CardContent className="flex items-center gap-3 py-4">
            <div className="rounded-full bg-green-100 dark:bg-green-900/30 p-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Total Revenue</p>
              <p className="text-xl font-bold text-green-600">{fmt(totals.revenue)}</p>
              <p className="text-[10px] text-muted-foreground">All money that came into your business</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 py-4">
            <div className="rounded-full bg-red-100 dark:bg-red-900/30 p-2">
              <TrendingDown className="h-5 w-5 text-red-600" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Total Expenses</p>
              <p className="text-xl font-bold text-red-600">{fmt(totals.expenses)}</p>
              <p className="text-[10px] text-muted-foreground">All money you spent on suppliers, staff, etc.</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 py-4">
            <div className={`rounded-full p-2 ${totals.net_profit >= 0 ? "bg-green-100 dark:bg-green-900/30" : "bg-red-100 dark:bg-red-900/30"}`}>
              <DollarSign className={`h-5 w-5 ${totals.net_profit >= 0 ? "text-green-600" : "text-red-600"}`} />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Net Profit</p>
              <p className={`text-xl font-bold ${totals.net_profit >= 0 ? "text-green-600" : "text-red-600"}`}>
                {fmt(totals.net_profit)}
              </p>
              <p className="text-[10px] text-muted-foreground">{margin.toFixed(1)}% margin — {totals.net_profit >= 0 ? "you kept this much of every sale" : "you are spending more than you earn"}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 py-4">
            <div className="rounded-full bg-orange-100 dark:bg-orange-900/30 p-2">
              <Receipt className="h-5 w-5 text-orange-600" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Total Tax Burden</p>
              <p className="text-xl font-bold text-orange-600">{fmt(totals.total_tax_burden || 0)}</p>
              <p className="text-[10px] text-muted-foreground">Total taxes across VAT, WHT, CIT, PAYE, and customs</p>
              {vat.net_liability !== 0 && (
                <p className="text-[10px] text-muted-foreground">
                  VAT {vat.net_liability > 0 ? "owed" : "refund"}: {fmt(Math.abs(vat.net_liability))}
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Monthly Trend Bar Chart */}
      {data.monthly_trend.length > 0 && (
        <Card className="col-span-full">
          <CardHeader>
            <CardTitle className="text-base">Monthly Revenue vs Expenses</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6 md:grid-cols-2">
              <div>
                <p className="text-xs text-muted-foreground mb-2 text-center">Revenue</p>
                <BarChart
                  data={data.monthly_trend.map((m) => ({
                    label: m.period,
                    value: m.revenue,
                    color: "#10b981",
                  }))}
                  height={180}
                  formatValue={fmt}
                />
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-2 text-center">Expenses</p>
                <BarChart
                  data={data.monthly_trend.map((m) => ({
                    label: m.period,
                    value: m.expenses,
                    color: "#ef4444",
                  }))}
                  height={180}
                  formatValue={fmt}
                />
              </div>
            </div>
            {/* Net profit trend */}
            <div className="mt-4 border-t pt-4">
              <p className="text-xs text-muted-foreground mb-2 text-center">Net Profit / Loss by Month</p>
              <BarChart
                data={data.monthly_trend.map((m) => ({
                  label: m.period,
                  value: m.net,
                  color: m.net >= 0 ? "#10b981" : "#ef4444",
                }))}
                height={140}
                formatValue={fmt}
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Pie Charts Row */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 col-span-full">
        {/* Expense by Vendor */}
        {data.expense_by_vendor.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Expenses by Vendor</CardTitle>
            </CardHeader>
            <CardContent className="flex justify-center">
              <PieChart data={data.expense_by_vendor} size={200} label="Expenses" donut />
            </CardContent>
          </Card>
        )}

        {/* Revenue by Source */}
        {data.revenue_by_source.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Revenue by Source</CardTitle>
            </CardHeader>
            <CardContent className="flex justify-center">
              <PieChart data={data.revenue_by_source} size={200} label="Revenue" donut />
            </CardContent>
          </Card>
        )}

        {/* Revenue vs Expense Split */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Revenue vs Expenses</CardTitle>
          </CardHeader>
          <CardContent className="flex justify-center">
            <PieChart
              data={[
                { name: "Revenue", value: totals.revenue },
                { name: "Expenses", value: totals.expenses },
              ]}
              size={200}
            />
          </CardContent>
        </Card>

        {/* Tax Breakdown (all tax types) */}
        {data.tax_breakdown && data.tax_breakdown.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Tax Breakdown</CardTitle>
            </CardHeader>
            <CardContent className="flex justify-center">
              <PieChart
                data={data.tax_breakdown}
                size={200}
                donut
                label="Taxes"
              />
            </CardContent>
          </Card>
        )}

        {/* VAT Breakdown */}
        {(vat.collected > 0 || vat.paid > 0) && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">VAT Breakdown</CardTitle>
            </CardHeader>
            <CardContent className="flex justify-center">
              <PieChart
                data={[
                  { name: "VAT Collected", value: vat.collected },
                  { name: "VAT Paid", value: vat.paid },
                ]}
                size={200}
                donut
                label="VAT"
              />
            </CardContent>
          </Card>
        )}

        {/* Currency Distribution */}
        {data.currency_breakdown.length > 1 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Currency Distribution</CardTitle>
            </CardHeader>
            <CardContent className="flex justify-center">
              <PieChart
                data={data.currency_breakdown.map((c) => ({
                  name: c.currency,
                  value: c.total,
                }))}
                size={200}
                donut
                label="Currencies"
              />
            </CardContent>
          </Card>
        )}

        {/* Category Breakdown */}
        {data.category_breakdown.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Document Categories</CardTitle>
            </CardHeader>
            <CardContent className="flex justify-center">
              <PieChart
                data={data.category_breakdown.map((c) => ({
                  name: c.name,
                  value: c.count,
                }))}
                size={200}
              />
            </CardContent>
          </Card>
        )}
      </div>

      {/* Vendor Expense Table */}
      {data.expense_by_vendor.length > 0 && (
        <Card className="col-span-full">
          <CardHeader>
            <CardTitle className="text-base">Top Vendors by Expense</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {data.expense_by_vendor.map((v, i) => {
                const pct = totals.expenses > 0 ? (v.value / totals.expenses) * 100 : 0;
                return (
                  <div key={i} className="flex items-center gap-3">
                    <span className="text-xs w-32 truncate" title={v.name}>{v.name}</span>
                    <div className="flex-1 bg-muted rounded h-5 overflow-hidden">
                      <div
                        className="h-full rounded transition-all"
                        style={{
                          width: `${pct}%`,
                          backgroundColor: pct > 40 ? "#ef4444" : pct > 25 ? "#f59e0b" : "#3b82f6",
                          minWidth: 4,
                        }}
                      />
                    </div>
                    <span className="text-xs w-24 text-right font-medium">{fmt(v.value)}</span>
                    <span className="text-xs w-12 text-right text-muted-foreground">{pct.toFixed(0)}%</span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </>
  );
}
