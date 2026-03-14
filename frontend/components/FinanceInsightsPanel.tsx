/**
 * FinanceInsightsPanel — AI-generated financial analysis panel covering
 * profitability, cashflow, vendor analysis, and multi-tax breakdowns
 * (VAT, WHT, CIT, PAYE, customs). Supports on-demand refresh.
 */
"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Sparkles,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  AlertCircle,
  Info,
  Loader2,
  ChevronRight,
  Receipt,
  PiggyBank,
  BarChart3,
  Building2,
} from "lucide-react";

interface Highlight {
  type: "positive" | "warning" | "critical" | "info";
  title: string;
  detail: string;
}

interface TaxInsights {
  vat_position: string;
  wht_position?: string;
  cit_position?: string;
  paye_position?: string;
  customs_position?: string;
  tax_tips: string[];
  estimated_vat_liability: number;
  total_tax_burden?: number;
  effective_tax_rate?: number;
  filing_reminder: string | null;
}

interface FinanceInsightsData {
  summary: string;
  highlights: Highlight[];
  tax_insights: TaxInsights;
  cashflow_analysis: string;
  profitability_analysis: string;
  vendor_insights: string;
  next_steps: string[];
  confidence: string;
}

interface FinanceInsightsPanelProps {
  insights: FinanceInsightsData | null;
  loading: boolean;
  onRefresh: () => void;
  refreshing: boolean;
}

export default function FinanceInsightsPanel({
  insights,
  loading,
  onRefresh,
  refreshing,
}: FinanceInsightsPanelProps) {
  const iconFor = (type: string) => {
    switch (type) {
      case "positive":
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case "critical":
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      case "warning":
        return <AlertCircle className="h-4 w-4 text-yellow-600" />;
      default:
        return <Info className="h-4 w-4 text-blue-600" />;
    }
  };

  const borderFor = (type: string) => {
    switch (type) {
      case "positive":
        return "border-l-green-500";
      case "critical":
        return "border-l-red-500";
      case "warning":
        return "border-l-yellow-500";
      default:
        return "border-l-blue-500";
    }
  };

  if (loading) {
    return (
      <Card className="col-span-full">
        <CardContent className="flex items-center gap-2 py-8 text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span className="text-sm">Generating financial insights…</span>
        </CardContent>
      </Card>
    );
  }

  if (!insights) {
    return (
      <Card className="col-span-full">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <CardTitle>AI Financial Insights</CardTitle>
            </div>
            <Button variant="outline" size="sm" onClick={onRefresh} disabled={refreshing}>
              {refreshing ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Sparkles className="h-4 w-4 mr-2" />}
              {refreshing ? "Analysing…" : "Generate Insights"}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-center py-6">
            <Sparkles className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
            <p className="text-sm font-medium">No financial insights yet</p>
            <p className="text-xs text-muted-foreground mt-1">
              Upload financial documents and click &quot;Generate Insights&quot; for an AI-powered analysis of your finances, taxes, and cash flow.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const tax = insights.tax_insights || {};

  return (
    <Card className="col-span-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            <CardTitle>AI Financial Insights</CardTitle>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-muted-foreground capitalize">
              Confidence: {insights.confidence}
            </span>
            <Button variant="outline" size="sm" onClick={onRefresh} disabled={refreshing}>
              {refreshing ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Sparkles className="h-4 w-4 mr-2" />}
              {refreshing ? "Analysing…" : "Refresh"}
            </Button>
          </div>
        </div>
        <CardDescription>
          AI-generated analysis of your finances, taxation, and cash flow
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Summary */}
        <div className="rounded-lg bg-primary/5 p-4">
          <p className="text-sm leading-relaxed">{insights.summary}</p>
        </div>

        {/* Key Highlights */}
        {insights.highlights.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Key Findings
            </p>
            {insights.highlights.map((h, i) => (
              <div
                key={i}
                className={`border-l-4 ${borderFor(h.type)} rounded-r-lg bg-card p-3 flex items-start gap-3`}
              >
                <div className="mt-0.5">{iconFor(h.type)}</div>
                <div>
                  <p className="text-sm font-medium">{h.title}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{h.detail}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Analysis Grid */}
        <div className="grid gap-4 md:grid-cols-2">
          {/* Profitability */}
          {insights.profitability_analysis && (
            <div className="rounded-lg border p-4 space-y-1">
              <div className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-primary" />
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Profitability</p>
              </div>
              <p className="text-sm">{insights.profitability_analysis}</p>
            </div>
          )}

          {/* Cashflow */}
          {insights.cashflow_analysis && (
            <div className="rounded-lg border p-4 space-y-1">
              <div className="flex items-center gap-2">
                <TrendingDown className="h-4 w-4 text-primary" />
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Cash Flow Trend</p>
              </div>
              <p className="text-sm">{insights.cashflow_analysis}</p>
            </div>
          )}

          {/* Vendor Insights */}
          {insights.vendor_insights && (
            <div className="rounded-lg border p-4 space-y-1">
              <div className="flex items-center gap-2">
                <Building2 className="h-4 w-4 text-primary" />
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Vendor Analysis</p>
              </div>
              <p className="text-sm">{insights.vendor_insights}</p>
            </div>
          )}

          {/* VAT Position */}
          {tax.vat_position && (
            <div className="rounded-lg border p-4 space-y-1">
              <div className="flex items-center gap-2">
                <Receipt className="h-4 w-4 text-primary" />
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">VAT Position</p>
              </div>
              <p className="text-sm">{tax.vat_position}</p>
              {tax.estimated_vat_liability !== 0 && (
                <p className="text-xs font-medium mt-1">
                  Estimated VAT {tax.estimated_vat_liability > 0 ? "liability" : "refund"}:{" "}
                  <span className={tax.estimated_vat_liability > 0 ? "text-red-600" : "text-green-600"}>
                    {Math.abs(tax.estimated_vat_liability).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </span>
                </p>
              )}
            </div>
          )}

          {/* WHT Position */}
          {tax.wht_position && (
            <div className="rounded-lg border p-4 space-y-1">
              <div className="flex items-center gap-2">
                <Receipt className="h-4 w-4 text-primary" />
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Withholding Tax</p>
              </div>
              <p className="text-sm">{tax.wht_position}</p>
            </div>
          )}

          {/* CIT Position */}
          {tax.cit_position && (
            <div className="rounded-lg border p-4 space-y-1">
              <div className="flex items-center gap-2">
                <Receipt className="h-4 w-4 text-primary" />
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Corporate Income Tax</p>
              </div>
              <p className="text-sm">{tax.cit_position}</p>
            </div>
          )}

          {/* PAYE Position */}
          {tax.paye_position && (
            <div className="rounded-lg border p-4 space-y-1">
              <div className="flex items-center gap-2">
                <Receipt className="h-4 w-4 text-primary" />
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">PAYE / Payroll Tax</p>
              </div>
              <p className="text-sm">{tax.paye_position}</p>
            </div>
          )}

          {/* Customs Position */}
          {tax.customs_position && (
            <div className="rounded-lg border p-4 space-y-1">
              <div className="flex items-center gap-2">
                <Receipt className="h-4 w-4 text-primary" />
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Customs / Import Levy</p>
              </div>
              <p className="text-sm">{tax.customs_position}</p>
            </div>
          )}
        </div>

        {/* Total Tax Burden */}
        {(tax.total_tax_burden ?? 0) > 0 && (
          <div className="rounded-lg bg-orange-50 dark:bg-orange-950/20 border border-orange-200 dark:border-orange-800 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Total Tax Burden</p>
                <p className="text-lg font-semibold text-orange-700 dark:text-orange-300">
                  {tax.total_tax_burden!.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </p>
              </div>
              {(tax.effective_tax_rate ?? 0) > 0 && (
                <div className="text-right">
                  <p className="text-xs text-muted-foreground">Effective Tax Rate</p>
                  <p className="text-lg font-semibold text-orange-700 dark:text-orange-300">
                    {tax.effective_tax_rate!.toFixed(1)}%
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tax Tips */}
        {tax.tax_tips && tax.tax_tips.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <PiggyBank className="h-4 w-4 text-primary" />
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Tax Tips</p>
            </div>
            {tax.tax_tips.map((tip: string, i: number) => (
              <div key={i} className="flex items-start gap-2 pl-1">
                <ChevronRight className="h-4 w-4 text-primary mt-0.5 shrink-0" />
                <p className="text-sm">{tip}</p>
              </div>
            ))}
            {tax.filing_reminder && (
              <div className="rounded-lg bg-yellow-50 dark:bg-yellow-950/20 border border-yellow-200 dark:border-yellow-800 p-3 mt-2">
                <p className="text-xs text-yellow-800 dark:text-yellow-200">{tax.filing_reminder}</p>
              </div>
            )}
          </div>
        )}

        {/* Next Steps */}
        {insights.next_steps.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Recommended Next Steps
            </p>
            {insights.next_steps.map((step, i) => (
              <div key={i} className="flex items-start gap-2">
                <ChevronRight className="h-4 w-4 text-primary mt-0.5 shrink-0" />
                <p className="text-sm">{step}</p>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
