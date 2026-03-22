/**
 * @file StockAlertBadge — Visual indicator for low stock and expiry warnings.
 * Shows severity-coloured badges for inventory alert states.
 */
"use client";

import { AlertTriangle, XCircle, Info } from "lucide-react";

interface StockAlertBadgeProps {
  severity: "critical" | "warning" | "info";
  label?: string;
}

const SEVERITY_STYLES: Record<string, { bg: string; text: string; icon: typeof AlertTriangle }> = {
  critical: { bg: "bg-red-100", text: "text-red-700", icon: XCircle },
  warning: { bg: "bg-amber-100", text: "text-amber-700", icon: AlertTriangle },
  info: { bg: "bg-blue-100", text: "text-blue-700", icon: Info },
};

export default function StockAlertBadge({ severity, label }: StockAlertBadgeProps) {
  const style = SEVERITY_STYLES[severity] || SEVERITY_STYLES.info;
  const Icon = style.icon;
  const defaultLabel = severity === "critical" ? "Out of Stock" : severity === "warning" ? "Low Stock" : "OK";

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${style.bg} ${style.text}`}
    >
      <Icon className="h-3 w-3" />
      {label || defaultLabel}
    </span>
  );
}
