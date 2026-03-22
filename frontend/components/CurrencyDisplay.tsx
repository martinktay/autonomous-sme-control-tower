/**
 * @file CurrencyDisplay — Formatted currency display supporting NGN, USD, GBP, EUR.
 * Renders amounts with proper currency symbols and locale-aware formatting.
 */
"use client";

interface CurrencyDisplayProps {
  amount: number;
  currency?: "NGN" | "USD" | "GBP" | "EUR";
  className?: string;
  compact?: boolean;
}

const CURRENCY_CONFIG: Record<string, { symbol: string; locale: string }> = {
  NGN: { symbol: "₦", locale: "en-NG" },
  USD: { symbol: "$", locale: "en-US" },
  GBP: { symbol: "£", locale: "en-GB" },
  EUR: { symbol: "€", locale: "de-DE" },
};

function formatAmount(amount: number, locale: string, compact: boolean): string {
  if (compact && Math.abs(amount) >= 1_000_000) {
    return (amount / 1_000_000).toFixed(1) + "M";
  }
  if (compact && Math.abs(amount) >= 1_000) {
    return (amount / 1_000).toFixed(1) + "K";
  }
  return amount.toLocaleString(locale, {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  });
}

export default function CurrencyDisplay({
  amount,
  currency = "NGN",
  className = "",
  compact = false,
}: CurrencyDisplayProps) {
  const config = CURRENCY_CONFIG[currency] || CURRENCY_CONFIG.NGN;
  const formatted = formatAmount(amount, config.locale, compact);
  const isNegative = amount < 0;

  return (
    <span className={`tabular-nums ${isNegative ? "text-red-600" : ""} ${className}`}>
      {config.symbol}
      {formatted}
    </span>
  );
}
