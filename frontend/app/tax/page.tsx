"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useOrg } from "@/lib/org-context";
import { generateTaxReport, getVatSummary } from "@/lib/api";
import {
  FileText, Calculator, AlertTriangle, CheckCircle2,
  Download, Loader2, Calendar, Building2, Receipt,
  Users, Info, ChevronDown, ChevronRight, Globe,
} from "lucide-react";

interface TaxReport {
  report_id: string;
  fiscal_year: number;
  total_revenue: number;
  total_expenses: number;
  gross_profit: number;
  net_profit: number;
  cit_applicable: boolean;
  cit_rate: number;
  cit_amount: number;
  cit_note: string;
  vat_rate: number;
  vatable_revenue: number;
  vat_collected: number;
  vat_on_purchases: number;
  vat_payable: number;
  wht_payments: number;
  wht_rate: number;
  wht_deducted: number;
  total_staff_costs: number;
  paye_estimate: number;
  total_tax_liability: number;
  filing_deadline: string;
  penalties_if_late: string;
  revenue_by_category: Record<string, number>;
  expense_by_category: Record<string, number>;
}

interface VatQuarter {
  quarter: number;
  period: string;
  total_revenue: number;
  total_expenses: number;
  vat_output: number;
  vat_input_credit: number;
  vat_payable: number;
  transaction_count: number;
}

const COUNTRIES = [
  { code: "NG", name: "Nigeria", flag: "\u{1F1F3}\u{1F1EC}", symbol: "\u20A6", authority: "FIRS" },
  { code: "GH", name: "Ghana", flag: "\u{1F1EC}\u{1F1ED}", symbol: "GH\u20B5", authority: "GRA" },
  { code: "KE", name: "Kenya", flag: "\u{1F1F0}\u{1F1EA}", symbol: "KSh", authority: "KRA" },
  { code: "ZA", name: "South Africa", flag: "\u{1F1FF}\u{1F1E6}", symbol: "R", authority: "SARS" },
  { code: "RW", name: "Rwanda", flag: "\u{1F1F7}\u{1F1FC}", symbol: "FRw", authority: "RRA" },
  { code: "GB", name: "United Kingdom", flag: "\u{1F1EC}\u{1F1E7}", symbol: "\u00A3", authority: "HMRC" },
];

function formatCurrency(amount: number, countryCode: string): string {
  const country = COUNTRIES.find((c) => c.code === countryCode);
  const sym = country?.symbol || "\u20A6";
  return `${sym}${amount.toLocaleString("en", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default function TaxPage() {
  const { orgId } = useOrg();
  const currentYear = new Date().getFullYear();

  const [countryCode, setCountryCode] = useState("NG");
  const [fiscalYear, setFiscalYear] = useState(currentYear - 1);
  const [businessName, setBusinessName] = useState("");
  const [tin, setTin] = useState("");
  const [vatRegistered, setVatRegistered] = useState(false);
  const [hasEmployees, setHasEmployees] = useState(false);
  const [monthlyStaffCost, setMonthlyStaffCost] = useState(0);

  const [report, setReport] = useState<TaxReport | null>(null);
  const [vatQuarters, setVatQuarters] = useState<VatQuarter[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showBreakdown, setShowBreakdown] = useState(false);
  const [showVat, setShowVat] = useState(false);

  const selectedCountry = COUNTRIES.find((c) => c.code === countryCode) || COUNTRIES[0];

  const handleGenerate = async () => {
    setLoading(true);
    setError("");
    setReport(null);
    setVatQuarters([]);
    try {
      const data = await generateTaxReport(orgId, {
        fiscal_year: fiscalYear,
        business_name: businessName,
        tin: tin || undefined,
        vat_registered: vatRegistered,
        has_employees: hasEmployees,
        monthly_staff_cost: monthlyStaffCost,
        country_code: countryCode,
      });
      setReport(data);

      if (vatRegistered) {
        const quarters: VatQuarter[] = [];
        for (let q = 1; q <= 4; q++) {
          try {
            const vq = await getVatSummary(orgId, fiscalYear, q, countryCode);
            quarters.push(vq);
          } catch { /* skip */ }
        }
        setVatQuarters(quarters);
      }
    } catch (err: any) {
      setError(err.message || "Failed to generate report");
    } finally {
      setLoading(false);
    }
  };

  const fmt = (amount: number) => formatCurrency(amount, countryCode);

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-1">Tax & Compliance</h1>
        <p className="text-muted-foreground">
          Generate your annual tax report from your transaction data. Country-aware calculations.
        </p>
      </div>

      {/* Country Selector */}
      <Card>
        <CardContent className="pt-4 pb-4">
          <div className="flex items-center gap-3 flex-wrap">
            <Globe className="h-5 w-5 text-muted-foreground" />
            <span className="text-sm font-medium">Country:</span>
            <div className="flex gap-2 flex-wrap">
              {COUNTRIES.map((c) => (
                <button
                  key={c.code}
                  onClick={() => setCountryCode(c.code)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm border transition-colors ${
                    countryCode === c.code
                      ? "bg-primary text-primary-foreground border-primary"
                      : "hover:bg-accent border-border"
                  }`}
                >
                  <span>{c.flag}</span>
                  <span>{c.name}</span>
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tax Education Banner */}
      <Card className="border-blue-200 bg-blue-50/50">
        <CardContent className="pt-4 pb-4">
          <div className="flex gap-3">
            <Info className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm space-y-1">
              <p className="font-medium text-blue-900">
                {selectedCountry.flag} Tax overview for {selectedCountry.name} ({selectedCountry.authority})
              </p>
              <ul className="text-blue-800 space-y-0.5 list-disc list-inside">
                <li>Tax rates and thresholds are country-specific and applied automatically</li>
                <li>VAT rate: {report?.vat_rate ? `${(report.vat_rate * 100).toFixed(1)}%` : "varies by country"}</li>
                <li>Filing deadlines and penalties follow {selectedCountry.authority} rules</li>
                <li>All calculations use your uploaded transaction data</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Report Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calculator className="h-5 w-5" />
            Generate Annual Tax Report
          </CardTitle>
          <CardDescription>
            We calculate CIT, VAT, WHT, and PAYE using {selectedCountry.name} tax rules.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium block mb-1">Fiscal Year</label>
              <select value={fiscalYear} onChange={(e) => setFiscalYear(Number(e.target.value))} className="w-full border rounded-md px-3 py-2 text-sm" aria-label="Fiscal year">
                {[currentYear - 1, currentYear - 2, currentYear - 3, currentYear].map((y) => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium block mb-1">Business Name</label>
              <input type="text" value={businessName} onChange={(e) => setBusinessName(e.target.value)} placeholder="e.g. Ade's Trading Co" className="w-full border rounded-md px-3 py-2 text-sm" aria-label="Business name" />
            </div>
            <div>
              <label className="text-sm font-medium block mb-1">TIN (Tax ID Number)</label>
              <input type="text" value={tin} onChange={(e) => setTin(e.target.value)} placeholder="Optional" className="w-full border rounded-md px-3 py-2 text-sm" aria-label="Tax identification number" />
            </div>
            <div className="flex items-end gap-4">
              <label className="flex items-center gap-2 text-sm cursor-pointer">
                <input type="checkbox" checked={vatRegistered} onChange={(e) => setVatRegistered(e.target.checked)} className="rounded" />
                VAT Registered
              </label>
              <label className="flex items-center gap-2 text-sm cursor-pointer">
                <input type="checkbox" checked={hasEmployees} onChange={(e) => setHasEmployees(e.target.checked)} className="rounded" />
                Has Employees
              </label>
            </div>
          </div>

          {hasEmployees && (
            <div className="max-w-xs">
              <label className="text-sm font-medium block mb-1">Monthly Staff Cost ({selectedCountry.symbol})</label>
              <input type="number" value={monthlyStaffCost || ""} onChange={(e) => setMonthlyStaffCost(Number(e.target.value))} placeholder="Total monthly payroll" className="w-full border rounded-md px-3 py-2 text-sm" aria-label="Monthly staff cost" />
            </div>
          )}

          <Button onClick={handleGenerate} disabled={loading} className="gap-2">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />}
            {loading ? "Calculating..." : "Generate Tax Report"}
          </Button>

          {error && (
            <p className="text-sm text-red-600 flex items-center gap-1"><AlertTriangle className="h-4 w-4" /> {error}</p>
          )}
        </CardContent>
      </Card>

      {/* Tax Report Results */}
      {report && (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 print:grid-cols-4">
            <Card>
              <CardContent className="pt-4 pb-3 text-center">
                <p className="text-xs text-muted-foreground">Total Revenue</p>
                <p className="text-lg font-bold text-green-700">{fmt(report.total_revenue)}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-4 pb-3 text-center">
                <p className="text-xs text-muted-foreground">Total Expenses</p>
                <p className="text-lg font-bold text-red-600">{fmt(report.total_expenses)}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-4 pb-3 text-center">
                <p className="text-xs text-muted-foreground">Net Profit</p>
                <p className={`text-lg font-bold ${report.net_profit >= 0 ? "text-green-700" : "text-red-600"}`}>{fmt(report.net_profit)}</p>
              </CardContent>
            </Card>
            <Card className="border-amber-200 bg-amber-50/50">
              <CardContent className="pt-4 pb-3 text-center">
                <p className="text-xs text-amber-700 font-medium">Total Tax Due</p>
                <p className="text-lg font-bold text-amber-800">{fmt(report.total_tax_liability)}</p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Receipt className="h-5 w-5" /> Tax Computation — FY {report.fiscal_year}</CardTitle>
              <CardDescription>{report.cit_note}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* CIT */}
                <div className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2"><Building2 className="h-4 w-4 text-muted-foreground" /><span className="font-medium">Companies Income Tax (CIT)</span></div>
                    <span className="font-bold">{fmt(report.cit_amount)}</span>
                  </div>
                  <div className="text-sm text-muted-foreground space-y-1">
                    <p>Turnover: {fmt(report.total_revenue)} — {report.cit_note}</p>
                    {!report.cit_applicable && (
                      <p className="flex items-center gap-1 text-green-600"><CheckCircle2 className="h-3.5 w-3.5" /> CIT exempt — but you must still file annual returns</p>
                    )}
                    {report.cit_applicable && (
                      <p>Net profit {fmt(report.net_profit)} x {(report.cit_rate * 100).toFixed(0)}% = {fmt(report.cit_amount)}</p>
                    )}
                  </div>
                </div>

                {/* VAT */}
                <div className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2"><Receipt className="h-4 w-4 text-muted-foreground" /><span className="font-medium">VAT ({(report.vat_rate * 100).toFixed(1)}%)</span></div>
                    <span className="font-bold">{fmt(report.vat_payable)}</span>
                  </div>
                  <div className="text-sm text-muted-foreground space-y-1">
                    {!vatRegistered ? (
                      <p className="text-amber-600 flex items-center gap-1"><AlertTriangle className="h-3.5 w-3.5" /> Not VAT registered</p>
                    ) : (
                      <>
                        <p>Output VAT (on sales): {fmt(report.vat_collected)}</p>
                        <p>Input VAT credit: {fmt(report.vat_on_purchases)}</p>
                        <p>Net VAT payable: {fmt(report.vat_payable)}</p>
                      </>
                    )}
                  </div>
                </div>

                {/* WHT */}
                <div className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2"><Calculator className="h-4 w-4 text-muted-foreground" /><span className="font-medium">Withholding Tax (WHT — {(report.wht_rate * 100).toFixed(0)}%)</span></div>
                    <span className="font-bold">{fmt(report.wht_deducted)}</span>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    <p>Payments to suppliers/contractors: {fmt(report.wht_payments)}</p>
                    <p>WHT deducted: {fmt(report.wht_deducted)}</p>
                  </div>
                </div>

                {/* PAYE */}
                {hasEmployees && (
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2"><Users className="h-4 w-4 text-muted-foreground" /><span className="font-medium">PAYE (Staff Income Tax)</span></div>
                      <span className="font-bold">{fmt(report.paye_estimate)}</span>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      <p>Annual staff costs: {fmt(report.total_staff_costs)}</p>
                      <p>Estimated PAYE: {fmt(report.paye_estimate)}</p>
                      <p className="text-xs mt-1">Note: Actual PAYE depends on individual employee salaries. Consult a tax professional.</p>
                    </div>
                  </div>
                )}

                {/* Filing Deadline */}
                <div className="border rounded-lg p-4 border-red-200 bg-red-50/50">
                  <div className="flex items-center gap-2 mb-2"><Calendar className="h-4 w-4 text-red-600" /><span className="font-medium text-red-800">Filing Deadline</span></div>
                  <div className="text-sm text-red-700 space-y-1">
                    <p>CIT annual return due: <span className="font-bold">{report.filing_deadline}</span></p>
                    <p className="text-xs">{report.penalties_if_late}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Revenue/Expense Breakdown */}
          <Card>
            <CardHeader>
              <button onClick={() => setShowBreakdown(!showBreakdown)} className="flex items-center gap-2 w-full text-left">
                {showBreakdown ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                <CardTitle className="text-base">Revenue & Expense Breakdown</CardTitle>
              </button>
            </CardHeader>
            {showBreakdown && (
              <CardContent>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-sm font-medium mb-2 text-green-700">Revenue by Category</h4>
                    {Object.keys(report.revenue_by_category).length === 0 ? (
                      <p className="text-sm text-muted-foreground">No revenue data for this period</p>
                    ) : (
                      <div className="space-y-1">
                        {Object.entries(report.revenue_by_category).sort(([, a], [, b]) => b - a).map(([cat, amt]) => (
                          <div key={cat} className="flex justify-between text-sm">
                            <span className="capitalize">{cat.replace(/_/g, " ")}</span>
                            <span className="font-medium">{fmt(amt)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  <div>
                    <h4 className="text-sm font-medium mb-2 text-red-600">Expenses by Category</h4>
                    {Object.keys(report.expense_by_category).length === 0 ? (
                      <p className="text-sm text-muted-foreground">No expense data for this period</p>
                    ) : (
                      <div className="space-y-1">
                        {Object.entries(report.expense_by_category).sort(([, a], [, b]) => b - a).map(([cat, amt]) => (
                          <div key={cat} className="flex justify-between text-sm">
                            <span className="capitalize">{cat.replace(/_/g, " ")}</span>
                            <span className="font-medium">{fmt(amt)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            )}
          </Card>

          {/* Quarterly VAT */}
          {vatQuarters.length > 0 && (
            <Card>
              <CardHeader>
                <button onClick={() => setShowVat(!showVat)} className="flex items-center gap-2 w-full text-left">
                  {showVat ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                  <CardTitle className="text-base">Quarterly VAT Breakdown</CardTitle>
                </button>
              </CardHeader>
              {showVat && (
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm" role="table">
                      <thead>
                        <tr className="border-b text-left">
                          <th className="pb-2 font-medium">Quarter</th>
                          <th className="pb-2 font-medium text-right">Revenue</th>
                          <th className="pb-2 font-medium text-right">VAT Output</th>
                          <th className="pb-2 font-medium text-right">VAT Input</th>
                          <th className="pb-2 font-medium text-right">VAT Payable</th>
                        </tr>
                      </thead>
                      <tbody>
                        {vatQuarters.map((q) => (
                          <tr key={q.quarter} className="border-b last:border-0">
                            <td className="py-2">{q.period}</td>
                            <td className="py-2 text-right">{fmt(q.total_revenue)}</td>
                            <td className="py-2 text-right">{fmt(q.vat_output)}</td>
                            <td className="py-2 text-right text-green-600">({fmt(q.vat_input_credit)})</td>
                            <td className="py-2 text-right font-medium">{fmt(q.vat_payable)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              )}
            </Card>
          )}

          <div className="flex gap-3 print:hidden">
            <Button onClick={() => window.print()} variant="outline" className="gap-2">
              <Download className="h-4 w-4" /> Print / Save as PDF
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
