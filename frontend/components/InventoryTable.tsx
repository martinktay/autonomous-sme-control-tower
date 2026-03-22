/**
 * @file InventoryTable — Inventory list with stock alert badges and currency display.
 * Shows product name, SKU, quantity, reorder point, cost, selling price, and status.
 */
"use client";

import CurrencyDisplay from "@/components/CurrencyDisplay";
import StockAlertBadge from "@/components/StockAlertBadge";

interface InventoryItem {
  item_id: string;
  name: string;
  sku?: string;
  quantity_on_hand: number;
  reorder_point?: number;
  unit?: string;
  unit_cost?: number;
  selling_price?: number;
  category?: string;
}

interface InventoryTableProps {
  items: InventoryItem[];
  currency?: "NGN" | "USD" | "GBP" | "EUR";
}

function getStockSeverity(qty: number, reorder?: number): "critical" | "warning" | "info" {
  if (qty === 0) return "critical";
  if (reorder != null && qty <= reorder) return "warning";
  return "info";
}

export default function InventoryTable({ items, currency = "NGN" }: InventoryTableProps) {
  if (!items.length) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        No inventory items yet. Upload a stock report or add items manually.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b text-left text-muted-foreground">
            <th className="pb-3 pr-4 font-medium">Product</th>
            <th className="pb-3 pr-4 font-medium hidden sm:table-cell">SKU</th>
            <th className="pb-3 pr-4 font-medium text-right">Qty</th>
            <th className="pb-3 pr-4 font-medium text-right hidden md:table-cell">Reorder</th>
            <th className="pb-3 pr-4 font-medium text-right hidden md:table-cell">Cost</th>
            <th className="pb-3 pr-4 font-medium text-right hidden sm:table-cell">Price</th>
            <th className="pb-3 font-medium">Status</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => {
            const severity = getStockSeverity(item.quantity_on_hand, item.reorder_point);
            return (
              <tr key={item.item_id} className="border-b last:border-0 hover:bg-muted/50">
                <td className="py-3 pr-4">
                  <div className="font-medium">{item.name}</div>
                  {item.category && (
                    <div className="text-xs text-muted-foreground">{item.category}</div>
                  )}
                </td>
                <td className="py-3 pr-4 text-muted-foreground hidden sm:table-cell">
                  {item.sku || "—"}
                </td>
                <td className="py-3 pr-4 text-right tabular-nums">
                  {item.quantity_on_hand}
                  {item.unit && <span className="text-xs text-muted-foreground ml-1">{item.unit}</span>}
                </td>
                <td className="py-3 pr-4 text-right tabular-nums text-muted-foreground hidden md:table-cell">
                  {item.reorder_point ?? "—"}
                </td>
                <td className="py-3 pr-4 text-right hidden md:table-cell">
                  {item.unit_cost != null ? (
                    <CurrencyDisplay amount={item.unit_cost} currency={currency} />
                  ) : "—"}
                </td>
                <td className="py-3 pr-4 text-right hidden sm:table-cell">
                  {item.selling_price != null ? (
                    <CurrencyDisplay amount={item.selling_price} currency={currency} />
                  ) : "—"}
                </td>
                <td className="py-3">
                  {severity !== "info" ? (
                    <StockAlertBadge severity={severity} />
                  ) : (
                    <span className="text-xs text-green-600 font-medium">In Stock</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
