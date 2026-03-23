"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  BarChart3,
  TrendingUp,
  Users,
  ShoppingCart,
  Banknote,
  Package,
  Loader2,
} from "lucide-react";
import { useOrg } from "@/lib/org-context";
import { useAuth } from "@/lib/auth-context";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AnalyticsPage() {
  const { orgId } = useOrg();
  const { token } = useAuth();
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!orgId || !token) return;
    const headers: Record<string, string> = { Authorization: `Bearer ${token}`, "X-Org-ID": orgId };
    Promise.all([
      fetch(`${API}/api/transactions/summary`, { headers }).then((r) => r.ok ? r.json() : null),
      fetch(`${API}/api/finance/${orgId}/analytics`, { headers }).then((r) => r.ok ? r.json() : null),
    ])
      .then(([txnSummary, finAnalytics]) => {
        setSummary({
          txn: txnSummary,
          fin: finAnalytics?.analytics || null,
        });
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [orgId, token]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const txn = summary?.txn;
  const fin = summary?.fin;

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-1">Business Analytics</h1>
        <p className="text-muted-foreground">
          AI-powered insights across your revenue, expenses, customers, and operations.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <KpiCard icon={Banknote} label="Total Revenue" value={fmt(txn?.total_revenue)} color="text-green-600" />
        <KpiCard icon={ShoppingCart} label="Total Expenses" value={fmt(txn?.total_expenses)} color="text-red-500" />
        <KpiCard icon={TrendingUp} label="Net Profit" value={fmt(txn?.net_profit)} color={txn?.net_profit >= 0 ? "text-green-600" : "text-red-500"} />
        <KpiCard icon={Package} label="Transactions" value={txn?.transaction_count?.toLocaleString() || "0"} color="text-blue-600" />
      </div>

      {/* Analytics Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <BarChart3 className="h-4 w-4" /> Revenue by Source
            </CardTitle>
          </CardHeader>
          <CardContent>
            {fin?.revenue_by_source?.length ? (
              <div className="space-y-2">
                {fin.revenue_by_source.map((item: any) => (
                  <div key={item.name} className="flex justify-between text-sm">
                    <span className="truncate">{item.name}</span>
                    <span className="font-medium">₦{item.value?.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No revenue data yet. Upload transactions to see analytics.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <ShoppingCart className="h-4 w-4" /> Expense by Vendor
            </CardTitle>
          </CardHeader>
          <CardContent>
            {fin?.expense_by_vendor?.length ? (
              <div className="space-y-2">
                {fin.expense_by_vendor.map((item: any) => (
                  <div key={item.name} className="flex justify-between text-sm">
                    <span className="truncate">{item.name}</span>
                    <span className="font-medium">₦{item.value?.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No expense data yet.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Banknote className="h-4 w-4" /> Tax Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            {fin?.tax_breakdown?.length ? (
              <div className="space-y-2">
                {fin.tax_breakdown.map((item: any) => (
                  <div key={item.name} className="flex justify-between text-sm">
                    <span>{item.name}</span>
                    <span className="font-medium">₦{item.value?.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No tax data recorded yet.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <TrendingUp className="h-4 w-4" /> Monthly Trend
            </CardTitle>
          </CardHeader>
          <CardContent>
            {fin?.monthly_trend?.length ? (
              <div className="space-y-2">
                {fin.monthly_trend.slice(-6).map((item: any) => (
                  <div key={item.period} className="flex justify-between text-sm">
                    <span>{item.period}</span>
                    <span className={`font-medium ${item.net >= 0 ? "text-green-600" : "text-red-500"}`}>
                      ₦{item.net?.toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Upload more data to see trends.</p>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="text-center">
        <Link href="/analytics/marketing">
          <Button variant="outline" className="gap-2">
            <Users className="h-4 w-4" /> View Marketing Insights
          </Button>
        </Link>
      </div>
    </div>
  );
}

function KpiCard({ icon: Icon, label, value, color }: {
  icon: React.ComponentType<{ className?: string }>; label: string; value: string; color: string;
}) {
  return (
    <Card>
      <CardContent className="pt-4 pb-3">
        <div className="flex items-center gap-2 mb-1">
          <Icon className={`h-4 w-4 ${color}`} />
          <span className="text-xs text-muted-foreground">{label}</span>
        </div>
        <p className={`text-lg font-bold ${color}`}>{value}</p>
      </CardContent>
    </Card>
  );
}

function fmt(n: number | undefined): string {
  if (n === undefined || n === null) return "₦0";
  return `₦${n.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
}
