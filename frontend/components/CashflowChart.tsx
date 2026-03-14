/**
 * CashflowChart — Interactive cashflow visualisation with period toggles
 * (daily/weekly/monthly) and optional date-range filters.
 * Renders horizontal revenue vs expense bars for each period bucket.
 */
"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { getCashflow } from "@/lib/api";
import { useOrg } from "@/lib/org-context";

const PERIODS = ["daily", "weekly", "monthly"] as const;

export default function CashflowChart() {
  const { orgId } = useOrg();
  const [period, setPeriod] = useState<string>("monthly");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await getCashflow(orgId, period, startDate || undefined, endDate || undefined);
      setData(res.cashflow || []);
    } catch { setData([]); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, [orgId, period]);

  const maxVal = Math.max(...data.flatMap((d: any) => [d.revenue, d.expenses]), 1);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Cashflow</CardTitle>
        <div className="flex flex-wrap gap-2 mt-2">
          {PERIODS.map((p) => (
            <Button key={p} size="sm" variant={period === p ? "default" : "outline"} onClick={() => setPeriod(p)}>
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </Button>
          ))}
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)}
            className="border rounded px-2 py-1 text-sm" aria-label="Start date" />
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)}
            className="border rounded px-2 py-1 text-sm" aria-label="End date" />
          <Button size="sm" variant="outline" onClick={fetchData}>Apply</Button>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <p className="text-muted-foreground text-sm">Loading...</p>
        ) : data.length === 0 ? (
          <p className="text-muted-foreground text-sm">No cashflow data for this period.</p>
        ) : (
          <div className="space-y-3">
            {data.map((d: any) => (
              <div key={d.period} className="space-y-1">
                <p className="text-xs font-medium">{d.period}</p>
                <div className="flex items-center gap-2">
                  <span className="text-xs w-16 text-green-600">Revenue</span>
                  <div className="flex-1 bg-muted rounded h-4 overflow-hidden">
                    <div className="bg-green-500 h-full rounded" style={{ width: `${(d.revenue / maxVal) * 100}%` }} />
                  </div>
                  <span className="text-xs w-20 text-right">{d.revenue.toLocaleString()}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs w-16 text-red-600">Expenses</span>
                  <div className="flex-1 bg-muted rounded h-4 overflow-hidden">
                    <div className="bg-red-500 h-full rounded" style={{ width: `${(d.expenses / maxVal) * 100}%` }} />
                  </div>
                  <span className="text-xs w-20 text-right">{d.expenses.toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
