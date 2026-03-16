/**
 * PnlSummary — Compact profit-and-loss card showing revenue, expenses,
 * net profit, VAT summary, and multi-tax breakdown (WHT, CIT, PAYE, customs).
 * Fetches P&L data on mount and when date filters change.
 */
"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getPnl } from "@/lib/api";
import { useOrg } from "@/lib/org-context";

interface PnlSummaryProps {
  startDate?: string;
  endDate?: string;
}

export default function PnlSummary({ startDate, endDate }: PnlSummaryProps) {
  const { orgId } = useOrg();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    getPnl(orgId, startDate, endDate)
      .then((res) => setData(res.pnl))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [orgId, startDate, endDate]);

  if (loading) return <Card><CardContent className="py-6 text-sm text-muted-foreground">Loading P&L...</CardContent></Card>;
  if (!data) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Profit &amp; Loss</CardTitle>
        <p className="text-xs text-muted-foreground mt-1">How much you earned minus how much you spent. Green means profit, red means loss.</p>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-xs text-muted-foreground">Revenue</p>
            <p className="text-lg font-semibold text-green-600">{data.total_revenue?.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Expenses</p>
            <p className="text-lg font-semibold text-red-600">{data.total_expenses?.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Net Profit</p>
            <p className={`text-lg font-semibold ${data.net_profit >= 0 ? "text-green-600" : "text-red-600"}`}>
              {data.net_profit?.toLocaleString()}
            </p>
          </div>
        </div>

        {data.vat_summary && (data.vat_summary.total_vat_collected > 0 || data.vat_summary.total_vat_paid > 0) && (
          <div className="border-t pt-3 grid grid-cols-2 gap-4 text-center">
            <div>
              <p className="text-xs text-muted-foreground">VAT Collected</p>
              <p className="font-medium">{data.vat_summary.total_vat_collected?.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">VAT Paid</p>
              <p className="font-medium">{data.vat_summary.total_vat_paid?.toLocaleString()}</p>
            </div>
          </div>
        )}

        {data.tax_summary && data.tax_summary.total_tax_burden > 0 && (
          <div className="border-t pt-3 space-y-2">
            <p className="text-xs text-muted-foreground font-medium text-center">Tax Summary</p>
            <div className="grid grid-cols-2 gap-3 text-center">
              {data.tax_summary.withholding_tax > 0 && (
                <div>
                  <p className="text-[10px] text-muted-foreground">WHT</p>
                  <p className="text-sm font-medium">{data.tax_summary.withholding_tax.toLocaleString()}</p>
                </div>
              )}
              {data.tax_summary.corporate_income_tax > 0 && (
                <div>
                  <p className="text-[10px] text-muted-foreground">CIT</p>
                  <p className="text-sm font-medium">{data.tax_summary.corporate_income_tax.toLocaleString()}</p>
                </div>
              )}
              {data.tax_summary.paye_payroll > 0 && (
                <div>
                  <p className="text-[10px] text-muted-foreground">PAYE</p>
                  <p className="text-sm font-medium">{data.tax_summary.paye_payroll.toLocaleString()}</p>
                </div>
              )}
              {data.tax_summary.customs_levy > 0 && (
                <div>
                  <p className="text-[10px] text-muted-foreground">Customs</p>
                  <p className="text-sm font-medium">{data.tax_summary.customs_levy.toLocaleString()}</p>
                </div>
              )}
            </div>
            <div className="text-center pt-1 border-t">
              <p className="text-[10px] text-muted-foreground">Total Tax Burden</p>
              <p className="text-sm font-semibold text-orange-600">{data.tax_summary.total_tax_burden.toLocaleString()}</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
