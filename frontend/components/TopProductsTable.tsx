/**
 * @file TopProductsTable — Shows top-selling inventory items by quantity sold.
 * Designed for supermarket dashboard view.
 */
"use client";

import CurrencyDisplay from "@/components/CurrencyDisplay";

interface InventoryItem {
  item_id?: string;
  item_name?: string;
  name?: string;
  quantity_sold?: number;
  unit_price?: number;
  current_stock?: number;
  category?: string;
}

interface TopProductsTableProps {
  items: InventoryItem[];
  limit?: number;
}

export default function TopProductsTable({ items, limit = 5 }: TopProductsTableProps) {
  // Sort by quantity_sold descending, take top N
  const sorted = [...items]
    .filter((i) => (i.quantity_sold ?? 0) > 0)
    .sort((a, b) => (b.quantity_sold ?? 0) - (a.quantity_sold ?? 0))
    .slice(0, limit);

  if (sorted.length === 0) {
    return (
      <p className="text-sm text-muted-foreground py-4">
        No product sales data yet. Inventory items with sales will appear here.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-xs text-muted-foreground border-b">
            <th className="pb-2 font-medium">Product</th>
            <th className="pb-2 font-medium text-right">Sold</th>
            <th className="pb-2 font-medium text-right">Price</th>
            <th className="pb-2 font-medium text-right">Stock</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((item, i) => (
            <tr key={item.item_id || i} className="border-b last:border-0">
              <td className="py-2 truncate max-w-[140px]">
                {item.item_name || item.name || "—"}
              </td>
              <td className="py-2 text-right tabular-nums">
                {item.quantity_sold ?? 0}
              </td>
              <td className="py-2 text-right">
                <CurrencyDisplay amount={item.unit_price ?? 0} compact />
              </td>
              <td className="py-2 text-right">
                <span className={`tabular-nums ${(item.current_stock ?? 0) < 10 ? "text-red-600 font-medium" : ""}`}>
                  {item.current_stock ?? 0}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
