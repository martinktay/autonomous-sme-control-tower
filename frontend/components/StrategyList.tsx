/**
 * StrategyList — Displays AI-generated strategy recommendations with
 * predicted BSI improvement, confidence scores, and execute buttons.
 */
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface Strategy {
  strategy_id: string;
  description: string;
  predicted_bsi_improvement: number;
  confidence_score: number;
  automation_eligibility: boolean;
  reasoning?: string;
  created_at: string;
}

interface StrategyListProps {
  strategies: Strategy[];
  onExecute?: (strategyId: string) => void;
}

export function StrategyList({ strategies, onExecute }: StrategyListProps) {
  if (!strategies || strategies.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recommended Strategies</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">No strategies available</p>
        </CardContent>
      </Card>
    );
  }

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return "bg-green-500";
    if (score >= 0.6) return "bg-yellow-500";
    return "bg-red-500";
  };

  const getConfidenceLabel = (score: number) => {
    if (score >= 0.8) return "High";
    if (score >= 0.6) return "Medium";
    return "Low";
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recommended Strategies</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {strategies.map((strategy) => (
          <div
            key={strategy.strategy_id}
            className="rounded-lg border p-4 space-y-3"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="font-medium">{strategy.description}</p>
                {strategy.reasoning && (
                  <p className="text-sm text-muted-foreground mt-1">
                    {strategy.reasoning}
                  </p>
                )}
              </div>
              {strategy.automation_eligibility && (
                <Badge variant="outline" className="ml-2">
                  Auto-eligible
                </Badge>
              )}
            </div>

            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">Predicted Impact:</span>
                <span className="font-semibold text-green-600">
                  +{strategy.predicted_bsi_improvement.toFixed(1)} BSI
                </span>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">Confidence:</span>
                <div className="flex items-center gap-1">
                  <div
                    className={`h-2 w-2 rounded-full ${getConfidenceColor(
                      strategy.confidence_score
                    )}`}
                  ></div>
                  <span className="font-medium">
                    {getConfidenceLabel(strategy.confidence_score)} (
                    {(strategy.confidence_score * 100).toFixed(0)}%)
                  </span>
                </div>
              </div>
            </div>

            {onExecute && (
              <Button
                onClick={() => onExecute(strategy.strategy_id)}
                size="sm"
                className="w-full"
              >
                Execute Strategy
              </Button>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
