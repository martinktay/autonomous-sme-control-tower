"use client";

interface BarItem {
  label: string;
  value: number;
  color?: string;
}

interface BarChartProps {
  data: BarItem[];
  maxBars?: number;
  height?: number;
  formatValue?: (v: number) => string;
}

export default function BarChart({ data, maxBars = 10, height = 200, formatValue }: BarChartProps) {
  const items = data.slice(0, maxBars);
  const maxVal = Math.max(...items.map((d) => Math.abs(d.value)), 1);
  const fmt = formatValue || ((v: number) => v.toLocaleString());

  if (items.length === 0) {
    return <p className="text-sm text-muted-foreground text-center py-4">No data</p>;
  }

  return (
    <div className="w-full" style={{ minHeight: height }}>
      <div className="flex items-end gap-1.5 w-full" style={{ height: height - 32 }}>
        {items.map((d, i) => {
          const pct = (Math.abs(d.value) / maxVal) * 100;
          const color = d.color || (d.value >= 0 ? "#10b981" : "#ef4444");
          return (
            <div key={i} className="flex-1 flex flex-col items-center justify-end h-full min-w-0">
              <span className="text-[10px] text-muted-foreground mb-1 truncate w-full text-center" title={fmt(d.value)}>
                {fmt(d.value)}
              </span>
              <div
                className="w-full rounded-t transition-all"
                style={{ height: `${Math.max(pct, 2)}%`, backgroundColor: color, minHeight: 4 }}
                title={`${d.label}: ${fmt(d.value)}`}
              />
            </div>
          );
        })}
      </div>
      <div className="flex gap-1.5 mt-1">
        {items.map((d, i) => (
          <div key={i} className="flex-1 min-w-0">
            <p className="text-[10px] text-muted-foreground text-center truncate" title={d.label}>
              {d.label}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
