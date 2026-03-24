/**
 * @file Finance Export page (/finance/export) — Export financial data as CSV or XLSX.
 * Supports date range and category filters for targeted exports.
 */
"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { exportFinanceCsv, exportFinanceXlsx } from "@/lib/api";
import { useOrg } from "@/lib/org-context";
import { Download, Loader2, FileSpreadsheet, FileText } from "lucide-react";
import ReconciliationPanel from "@/components/ReconciliationPanel";
import Link from "next/link";

export default function ExportPage() {
  const { orgId } = useOrg();
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [category, setCategory] = useState("");
  const [downloading, setDownloading] = useState<"csv" | "xlsx" | null>(null);

  const handleDownload = async (format: "csv" | "xlsx") => {
    setDownloading(format);
    try {
      const exportFn = format === "xlsx" ? exportFinanceXlsx : exportFinanceCsv;
      const blob = await exportFn(
        orgId,
        startDate || undefined,
        endDate || undefined,
        category || undefined,
      );
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `finance_export_${orgId}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch { /* ignore */ }
    finally { setDownloading(null); }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-1">Export &amp; Reconciliation</h1>
          <p className="text-muted-foreground">Download your finance data or reconcile against bank statements.</p>
        </div>
        <Link href="/finance"><Button variant="outline">Back to Dashboard</Button></Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Export Finance Data</CardTitle>
          <CardDescription>Download as CSV (for spreadsheets) or Excel (.xlsx) format.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-3">
            <div>
              <label className="text-xs text-muted-foreground block mb-1">Start Date</label>
              <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)}
                className="border rounded px-2 py-1 text-sm" aria-label="Start date" />
            </div>
            <div>
              <label className="text-xs text-muted-foreground block mb-1">End Date</label>
              <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)}
                className="border rounded px-2 py-1 text-sm" aria-label="End date" />
            </div>
            <div>
              <label className="text-xs text-muted-foreground block mb-1">Category</label>
              <select value={category} onChange={(e) => setCategory(e.target.value)}
                className="border rounded px-2 py-1 text-sm" aria-label="Category filter">
                <option value="">All</option>
                <option value="revenue">Revenue</option>
                <option value="expense">Expense</option>
              </select>
            </div>
          </div>
          <div className="flex gap-3">
            <Button onClick={() => handleDownload("csv")} disabled={downloading !== null} variant="outline" className="gap-2">
              {downloading === "csv" ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />}
              Download CSV
            </Button>
            <Button onClick={() => handleDownload("xlsx")} disabled={downloading !== null} className="gap-2">
              {downloading === "xlsx" ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileSpreadsheet className="h-4 w-4" />}
              Download Excel
            </Button>
          </div>
        </CardContent>
      </Card>

      <ReconciliationPanel />
    </div>
  );
}
