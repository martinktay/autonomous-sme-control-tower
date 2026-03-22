/**
 * @file Locale-aware date formatting utility for African SME context.
 * Supports relative ("2 hours ago") and absolute ("15 Jan 2025") formats.
 */

const LOCALE_MAP: Record<string, string> = {
  NGN: "en-NG",
  USD: "en-US",
  GBP: "en-GB",
  EUR: "de-DE",
};

/** Get the locale string for a given currency code, defaulting to en-NG. */
function getLocale(currency?: string): string {
  return LOCALE_MAP[currency || "NGN"] || "en-NG";
}

/** Format a date string or Date as "15 Jan 2025". */
export function formatDate(
  date: string | Date | undefined | null,
  currency?: string,
): string {
  if (!date) return "—";
  const d = typeof date === "string" ? new Date(date) : date;
  if (isNaN(d.getTime())) return "—";
  return d.toLocaleDateString(getLocale(currency), {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

/** Format a date string or Date as "15 Jan 2025, 14:30". */
export function formatDateTime(
  date: string | Date | undefined | null,
  currency?: string,
): string {
  if (!date) return "—";
  const d = typeof date === "string" ? new Date(date) : date;
  if (isNaN(d.getTime())) return "—";
  return d.toLocaleDateString(getLocale(currency), {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/** Format as relative time: "2 hours ago", "3 days ago", "just now". */
export function formatRelative(date: string | Date | undefined | null): string {
  if (!date) return "—";
  const d = typeof date === "string" ? new Date(date) : date;
  if (isNaN(d.getTime())) return "—";

  const now = Date.now();
  const diffMs = now - d.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHr = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHr / 24);

  if (diffSec < 60) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  if (diffDay < 7) return `${diffDay}d ago`;
  return formatDate(d);
}
