/**
 * @file Inventory management page — Stock list, alerts, analytics.
 */
"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Package, AlertTriangle, TrendingUp, Plus } from "lucide-react";
import { useOrg } from "@/lib/org-context";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function InventoryPage() {
  const { orgId } = useOrg();
  const [items, setItems] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!orgId) return;
    setLoading(true);
    Promise.all([
      fetch(`${API}/api/inventory`, { headers: { "X-Org-ID": orgId } }).then((r) => r.ok ? r.json() : []),
      fetch(`${API}/api/inventory/alerts`, { headers: { "X-Org-ID": orgId } }).then((r) => r.ok ? r.json() : []),
      fetch(`${API}/api/inventory/analytics`, { headers: { "X-Org-ID": orgId } }).then((r) => r.ok ? r.json() : null),
    ])
      .then(([itemsData, alertsData, analyticsData]) => {
        setItems(itemsData);
        setAlerts(alertsData);
        setAnalytics(analyticsData);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [orgId]);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Stock & Inventory</h1>
          <p className="text-sm text-muted-foreground">Track your products, stock levels, and get low-stock alerts</p>
        </div>
        <Button className="gap-1">
          <Plus className="h-4 w-4" /> Add Item
        </Button>
      </div>

      {/* Analytics cards */}
      {analytics && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <Package className="h-8 w-8 text-primary" />
                <div>
                  <p className="text-2xl font-bold">{analytics.total_items}</p>
                  <p className="text-xs text-muted-foreground">Total Items</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-8 w-8 text-orange-500" />
                <div>
                  <p className="text-2xl font-bold">{analytics.low_stock_count}</p>
                  <p className="text-xs text-muted-foreground">Low Stock Items</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <TrendingUp className="h-8 w-8 text-green-500" />
                <div>
                  <p className="text-2xl font-bold">₦{analytics.estimated_stock_value?.toLocaleString()}</p>
                  <p className="text-xs text-muted-foreground">Stock Value</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Low stock alerts */}
      {alerts.length > 0 && (
        <Card className="mb-6 border-orange-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-orange-500" />
              Low Stock Alerts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {alerts.map((a: any) => (
                <div key={a.item_id} className="flex items-center justify-between text-sm p-2 rounded bg-orange-50">
                  <span className="font-medium">{a.name}</span>
                  <span className="text-muted-foreground">
                    {a.quantity_on_hand} left (reorder at {a.reorder_point})
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Items table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">All Items</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-sm text-muted-foreground py-8 text-center">Loading inventory...</p>
          ) : items.length === 0 ? (
            <p className="text-sm text-muted-foreground py-8 text-center">
              No inventory items yet. Upload a stock list or add items manually.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-2">Name</th>
                    <th className="text-right py-2 px-2">Qty</th>
                    <th className="text-right py-2 px-2">Unit Cost</th>
                    <th className="text-right py-2 px-2">Selling Price</th>
                    <th className="text-left py-2 px-2">Category</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((item: any) => (
                    <tr key={item.item_id} className="border-b">
                      <td className="py-2 px-2">{item.name}</td>
                      <td className="text-right py-2 px-2">{item.quantity_on_hand}</td>
                      <td className="text-right py-2 px-2">
                        {item.unit_cost ? `₦${Number(item.unit_cost).toLocaleString()}` : "—"}
                      </td>
                      <td className="text-right py-2 px-2">
                        {item.selling_price ? `₦${Number(item.selling_price).toLocaleString()}` : "—"}
                      </td>
                      <td className="py-2 px-2 text-muted-foreground">{item.category || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
