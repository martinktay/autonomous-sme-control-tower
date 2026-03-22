/**
 * @file SalesTrendChart — Simple bar chart showing daily/weekly sales trends.
 * Uses recharts. Designed for supermarket dashboard view.
 */
"use client";

import { useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

interface Transaction {
  amount: number;
  transaction_type: string;
  date: string;
}

interface SalesTrendChartProps {
  transactions: Transaction[];
}

export default function SalesTrendChart({ transactions }: SalesTrendChartProps) {
  const chartData = useMemo(() => {
    // Group revenue transactions by date (last 14 days)
    const now = new Date();
    const cutoff = new Date(now);
    cutoff.setDate(cutoff.getDate() - 14);

    const byDate: Record<string, number> = {};
    for (const t of transactions) {
      if (t.transaction_type !== "revenue") continue;
      const d = new Date(t.date);
      if (d < cutoff) continue;
      const key = d.toLocaleDateString("en-GB", { day: "2-digit", month: "short" });
      byDate[key] = (byDate[key] || 0) + (t.amount || 0);
    }

    return Object.entries(byDate)
      .map(([date, sales]) => ({ date, sales: Math.round(sales) }))
      .slice(-14);
  }, [transactions]);

  if (chartData.length === 0) {
    return (
      <p className="text-sm text-muted-foreground py-4">
        No recent sales data to chart. Revenue transactions from the last 14 days will appear here.
      </p>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={chartData} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 11 }} />
        <Tooltip
          formatter={(value: number) => [`₦${value.toLocaleString()}`, "Sales"]}
          contentStyle={{ fontSize: 12 }}
        />
        <Bar dataKey="sales" fill="#22c55e" radius={[3, 3, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
