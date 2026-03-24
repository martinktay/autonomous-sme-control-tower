/**
 * @file Forecasting page (/forecasting) — AI revenue, expense, and cash runway projections.
 * Shows cash runway risk level and detailed AI-generated financial forecasts.
 */
"use client";

import { useState, useEffect } from "react";
import { useOrg } from "@/lib/org-context";
import { getCashRunway, getFinanceForecast } from "@/lib/api";
import { TrendingUp, AlertTriangle, Loader2, Brain, Banknote } from "lucide-react";

export default function ForecastingPage() {
  const { orgId } = useOrg();
  const [runway, setRunway] = useState<any>(null);
  const [forecast, setForecast] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!orgId) return;
    setLoading(true);
    getCashRunway(orgId)
      .then(setRunway)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [orgId]);

  const runForecast = async () => {
    if (!orgId) return;
    setForecastLoading(true);
    try {
      const data = await getFinanceForecast(orgId);
      setForecast(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setForecastLoading(false);
    }
  };

  const riskColor = (risk: string) => {
    if (risk === "healthy") return "text-green-600 bg-green-50";
    if (risk === "caution") return "text-yellow-600 bg-yellow-50";
    return "text-red-600 bg-red-50";
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <TrendingUp className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-semibold">AI Forecasting</h1>
        </div>
        <button
          onClick={runForecast}
          disabled={forecastLoading}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
        >
          {forecastLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Brain className="h-4 w-4" />}
          {forecastLoading ? "Forecasting..." : "Full AI Forecast"}
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 mb-6 rounded-lg bg-destructive/10 text-destructive">
          <AlertTriangle className="h-4 w-4" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {/* Cash Runway */}
      {loading ? (
        <div className="flex items-center justify-center p-8">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : runway && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="border rounded-lg p-4 bg-card">
            <div className="text-sm text-muted-foreground">Cash Balance</div>
            <div className="text-xl font-semibold flex items-center gap-1">
              <Banknote className="h-4 w-4" />
              ₦{runway.current_balance?.toLocaleString()}
            </div>
          </div>
          <div className="border rounded-lg p-4 bg-card">
            <div className="text-sm text-muted-foreground">Monthly Burn</div>
            <div className="text-xl font-semibold">₦{runway.monthly_burn_rate?.toLocaleString()}</div>
          </div>
          <div className="border rounded-lg p-4 bg-card">
            <div className="text-sm text-muted-foreground">Days Remaining</div>
            <div className="text-xl font-semibold">{runway.days_remaining}</div>
          </div>
          <div className="border rounded-lg p-4 bg-card">
            <div className="text-sm text-muted-foreground">Risk Level</div>
            <span className={`inline-block px-3 py-1 rounded text-sm font-medium ${riskColor(runway.risk_level)}`}>
              {runway.risk_level}
            </span>
          </div>
        </div>
      )}

      {/* Full AI Forecast */}
      {forecast && (
        <>
          <div className="grid md:grid-cols-2 gap-6 mb-6">
            {forecast.revenue_forecast && (
              <div className="border rounded-lg p-4 bg-card">
                <h2 className="font-medium mb-3">Revenue Forecast</h2>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Trend</span>
                    <span className="font-medium">{forecast.revenue_forecast.trend}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Growth Rate</span>
                    <span className="font-medium">{forecast.revenue_forecast.growth_rate_pct}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Next 30 days</span>
                    <span>₦{forecast.revenue_forecast.next_30d?.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Next 60 days</span>
                    <span>₦{forecast.revenue_forecast.next_60d?.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Next 90 days</span>
                    <span>₦{forecast.revenue_forecast.next_90d?.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            )}
            {forecast.expense_forecast && (
              <div className="border rounded-lg p-4 bg-card">
                <h2 className="font-medium mb-3">Expense Forecast</h2>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Trend</span>
                    <span className="font-medium">{forecast.expense_forecast.trend}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Growth Rate</span>
                    <span className="font-medium">{forecast.expense_forecast.growth_rate_pct}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Next 30 days</span>
                    <span>₦{forecast.expense_forecast.next_30d?.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Next 60 days</span>
                    <span>₦{forecast.expense_forecast.next_60d?.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Next 90 days</span>
                    <span>₦{forecast.expense_forecast.next_90d?.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {forecast.recommendations?.length > 0 && (
            <div className="border rounded-lg p-4 mb-6 bg-card">
              <h2 className="font-medium mb-3">Recommendations</h2>
              <ul className="space-y-2">
                {forecast.recommendations.map((rec: string, i: number) => (
                  <li key={i} className="text-sm p-2 rounded bg-muted">{rec}</li>
                ))}
              </ul>
            </div>
          )}

          {forecast.summary && (
            <div className="p-4 rounded-lg bg-primary/5 text-sm">{forecast.summary}</div>
          )}
        </>
      )}
    </div>
  );
}
