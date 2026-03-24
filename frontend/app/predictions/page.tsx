/**
 * @file Predictions page (/predictions) — AI demand forecasting and reorder suggestions.
 * Shows inventory reorder urgency and AI-generated demand predictions.
 */
"use client";

import { useState, useEffect } from "react";
import { useOrg } from "@/lib/org-context";
import { getReorderSuggestions, getDemandForecast } from "@/lib/api";
import { TrendingUp, Package, AlertTriangle, Loader2, Brain, Clock } from "lucide-react";

interface ReorderItem {
  item_name: string;
  item_id: string;
  current_stock: number;
  avg_daily_sales: number;
  days_remaining: number;
  suggested_quantity: number;
  urgency: string;
}

export default function PredictionsPage() {
  const { orgId } = useOrg();
  const [suggestions, setSuggestions] = useState<ReorderItem[]>([]);
  const [forecast, setForecast] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!orgId) return;
    setLoading(true);
    getReorderSuggestions(orgId)
      .then((data) => setSuggestions(data.suggestions || []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [orgId]);

  const runForecast = async () => {
    if (!orgId) return;
    setForecastLoading(true);
    try {
      const data = await getDemandForecast(orgId);
      setForecast(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setForecastLoading(false);
    }
  };

  const urgencyBadge = (urgency: string) => {
    const styles: Record<string, string> = {
      immediate: "bg-red-100 text-red-700",
      soon: "bg-yellow-100 text-yellow-700",
      routine: "bg-blue-100 text-blue-700",
    };
    return styles[urgency] || "bg-gray-100 text-gray-700";
  };

  const riskBadge = (risk: string) => {
    const styles: Record<string, string> = {
      high: "bg-red-100 text-red-700",
      medium: "bg-yellow-100 text-yellow-700",
      low: "bg-green-100 text-green-700",
      none: "bg-gray-100 text-gray-500",
    };
    return styles[risk] || "bg-gray-100 text-gray-700";
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <TrendingUp className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-semibold">Inventory Predictions</h1>
        </div>
        <button
          onClick={runForecast}
          disabled={forecastLoading}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
        >
          {forecastLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Brain className="h-4 w-4" />}
          {forecastLoading ? "Forecasting..." : "AI Forecast"}
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 mb-6 rounded-lg bg-destructive/10 text-destructive">
          <AlertTriangle className="h-4 w-4" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {/* Reorder Suggestions */}
      <div className="border rounded-lg bg-card mb-6">
        <div className="p-4 border-b">
          <h2 className="font-medium flex items-center gap-2">
            <Package className="h-4 w-4" />
            Reorder Suggestions
          </h2>
        </div>
        {loading ? (
          <div className="flex items-center justify-center p-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : suggestions.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            No reorder suggestions right now. Stock levels look healthy.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="text-left p-3">Item</th>
                  <th className="text-center p-3">Stock</th>
                  <th className="text-center p-3">Daily Sales</th>
                  <th className="text-center p-3">Days Left</th>
                  <th className="text-center p-3">Order Qty</th>
                  <th className="text-center p-3">Urgency</th>
                </tr>
              </thead>
              <tbody>
                {suggestions.map((item) => (
                  <tr key={item.item_id} className="border-b last:border-0">
                    <td className="p-3 font-medium">{item.item_name}</td>
                    <td className="p-3 text-center">{item.current_stock}</td>
                    <td className="p-3 text-center text-muted-foreground">{item.avg_daily_sales}</td>
                    <td className="p-3 text-center">
                      <span className="flex items-center justify-center gap-1">
                        <Clock className="h-3 w-3" />
                        {item.days_remaining}
                      </span>
                    </td>
                    <td className="p-3 text-center font-medium">{item.suggested_quantity}</td>
                    <td className="p-3 text-center">
                      <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${urgencyBadge(item.urgency)}`}>
                        {item.urgency}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* AI Demand Forecast */}
      {forecast && (
        <>
          {forecast.predictions?.length > 0 && (
            <div className="border rounded-lg bg-card mb-6">
              <div className="p-4 border-b">
                <h2 className="font-medium">14-Day Demand Forecast</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="text-left p-3">Item</th>
                      <th className="text-center p-3">Stock</th>
                      <th className="text-center p-3">Predicted Demand</th>
                      <th className="text-center p-3">Trend</th>
                      <th className="text-center p-3">Stockout Risk</th>
                    </tr>
                  </thead>
                  <tbody>
                    {forecast.predictions.map((p: any, i: number) => (
                      <tr key={i} className="border-b last:border-0">
                        <td className="p-3 font-medium">{p.item_name}</td>
                        <td className="p-3 text-center">{p.current_stock}</td>
                        <td className="p-3 text-center">{p.predicted_demand_14d}</td>
                        <td className="p-3 text-center text-muted-foreground">{p.trend}</td>
                        <td className="p-3 text-center">
                          <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${riskBadge(p.stockout_risk)}`}>
                            {p.stockout_risk}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {forecast.seasonal_insights?.length > 0 && (
            <div className="border rounded-lg p-4 mb-6 bg-card">
              <h2 className="font-medium mb-3">Seasonal Insights</h2>
              <ul className="space-y-2">
                {forecast.seasonal_insights.map((insight: string, i: number) => (
                  <li key={i} className="text-sm p-2 rounded bg-muted">{insight}</li>
                ))}
              </ul>
            </div>
          )}

          {forecast.summary && (
            <div className="p-4 rounded-lg bg-primary/5 text-sm">
              {forecast.summary}
            </div>
          )}
        </>
      )}
    </div>
  );
}
