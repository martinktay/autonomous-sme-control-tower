/**
 * NSITrendChart — SVG line chart showing the Nova Stability Index
 * over time. Renders grid lines, data points with tooltips, and x-axis date labels.
 */
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface NSIDataPoint {
  timestamp: string;
  nsi_score: number;
}

interface NSITrendChartProps {
  data: NSIDataPoint[];
}

export function NSITrendChart({ data }: NSITrendChartProps) {
  // Simple line chart visualization
  const maxNSI = 100;
  const minNSI = 0;
  const chartHeight = 200;
  const chartWidth = 600;

  if (!data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>NSI Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">No trend data available</p>
        </CardContent>
      </Card>
    );
  }

  // Calculate points for the line chart
  const points = data.map((point, index) => {
    const x = (index / (data.length - 1)) * chartWidth;
    const y = chartHeight - ((point.nsi_score - minNSI) / (maxNSI - minNSI)) * chartHeight;
    return { x, y, nsi: point.nsi_score, timestamp: point.timestamp };
  });

  // Create path for line
  const pathData = points
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`)
    .join(" ");

  return (
    <Card>
      <CardHeader>
        <CardTitle>NSI Trend Over Time</CardTitle>
      </CardHeader>
      <CardContent>
        <svg
          width={chartWidth}
          height={chartHeight + 40}
          className="w-full"
          viewBox={`0 0 ${chartWidth} ${chartHeight + 40}`}
        >
          {/* Grid lines */}
          {[0, 25, 50, 75, 100].map((value) => {
            const y = chartHeight - ((value - minNSI) / (maxNSI - minNSI)) * chartHeight;
            return (
              <g key={value}>
                <line
                  x1={0}
                  y1={y}
                  x2={chartWidth}
                  y2={y}
                  stroke="#e5e7eb"
                  strokeWidth={1}
                />
                <text x={-5} y={y + 4} fontSize={12} fill="#6b7280" textAnchor="end">
                  {value}
                </text>
              </g>
            );
          })}

          {/* Line chart */}
          <path
            d={pathData}
            fill="none"
            stroke="#3b82f6"
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Data points */}
          {points.map((point, index) => (
            <g key={index}>
              <circle cx={point.x} cy={point.y} r={4} fill="#3b82f6" />
              <title>
                {new Date(point.timestamp).toLocaleDateString()}: NSI {point.nsi.toFixed(1)}
              </title>
            </g>
          ))}

          {/* X-axis labels */}
          {points.map((point, index) => {
            if (index % Math.ceil(points.length / 5) === 0 || index === points.length - 1) {
              return (
                <text
                  key={`label-${index}`}
                  x={point.x}
                  y={chartHeight + 20}
                  fontSize={10}
                  fill="#6b7280"
                  textAnchor="middle"
                >
                  {new Date(point.timestamp).toLocaleDateString(undefined, {
                    month: "short",
                    day: "numeric",
                  })}
                </text>
              );
            }
            return null;
          })}
        </svg>

        {/* Legend */}
        <div className="mt-4 flex items-center justify-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-blue-500"></div>
            <span className="text-muted-foreground">NSI Score</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
