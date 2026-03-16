/**
 * NSICard — Displays the Nova Stability Index score with health badge,
 * trend indicator, progress bar, and confidence/timestamp metadata.
 * Handles loading and empty-data states gracefully.
 */
"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Minus, Loader2 } from "lucide-react";

interface NsiCardProps {
  nsi: number | null;
  confidence?: string;
  trend?: number;
  timestamp?: string;
  loading?: boolean;
}

export default function NSICard({ 
  nsi, 
  confidence = "medium", 
  trend, 
  timestamp, 
  loading 
}: NsiCardProps) {
  const getHealthColor = (score: number) => {
    if (score >= 70) return "text-green-600";
    if (score >= 40) return "text-yellow-600";
    return "text-red-600";
  };

  const getHealthLabel = (score: number) => {
    if (score >= 70) return "Healthy";
    if (score >= 40) return "Moderate";
    return "At Risk";
  };

  const getTrendIcon = () => {
    if (!trend) return <Minus className="h-4 w-4" />;
    if (trend > 0) return <TrendingUp className="h-4 w-4 text-green-600" />;
    return <TrendingDown className="h-4 w-4 text-red-600" />;
  };

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Nova Stability Index</CardTitle>
          <CardDescription>Overall operational health score</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-40">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    );
  }

  if (nsi === null) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Nova Stability Index</CardTitle>
          <CardDescription>Overall operational health score</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">No data available</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Nova Stability Index</CardTitle>
          <Badge variant={nsi >= 70 ? "default" : nsi >= 40 ? "secondary" : "destructive"}>
            {getHealthLabel(nsi)}
          </Badge>
        </div>
        <CardDescription>
          Your overall business health score out of 100. Above 70 is healthy, 40–69 needs attention, below 40 means act quickly.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-baseline justify-between">
          <div className={`text-6xl font-bold ${getHealthColor(nsi)}`}>
            {nsi.toFixed(1)}
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            {getTrendIcon()}
            {trend !== undefined && (
              <span>{trend > 0 ? '+' : ''}{trend.toFixed(1)}</span>
            )}
          </div>
        </div>

        <Progress 
          value={nsi} 
          className="h-3"
        />

        <div className="grid grid-cols-2 gap-4 pt-4 text-sm">
          <div>
            <p className="text-muted-foreground">Confidence</p>
            <p className="font-medium capitalize">{confidence}</p>
          </div>
          {timestamp && (
            <div>
              <p className="text-muted-foreground">Last Updated</p>
              <p className="font-medium">{new Date(timestamp).toLocaleTimeString()}</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
