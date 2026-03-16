/**
 * RiskPanel — Displays a ranked list of operational risks identified
 * by the AI risk-diagnosis agent. Colour-coded by severity (critical → low).
 */
"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, AlertCircle, Info, Loader2, ShieldCheck } from "lucide-react";

interface Risk {
  description?: string;
  risk?: string;
  severity: string;
  category?: string;
}

interface RiskPanelProps {
  risks: Risk[];
  loading?: boolean;
}

export default function RiskPanel({ risks, loading }: RiskPanelProps) {
  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical":
      case "high":
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      case "medium":
        return <AlertCircle className="h-4 w-4 text-yellow-600" />;
      default:
        return <Info className="h-4 w-4 text-blue-600" />;
    }
  };

  const getSeverityVariant = (severity: string): "default" | "secondary" | "destructive" | "outline" => {
    switch (severity.toLowerCase()) {
      case "critical":
      case "high":
        return "destructive";
      case "medium":
        return "secondary";
      default:
        return "outline";
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Top Operational Risks</CardTitle>
        <CardDescription>
          Problems the AI found in your business data, ranked by how urgent they are. Red means act now, yellow means keep an eye on it.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center gap-2 text-muted-foreground py-4">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">Checking for risks…</span>
          </div>
        ) : risks.length === 0 ? (
          <div className="flex flex-col items-center py-6 text-center">
            <ShieldCheck className="h-8 w-8 text-green-500 mb-2" />
            <p className="text-sm font-medium">No risks found</p>
            <p className="text-xs text-muted-foreground mt-1">Upload more data or run an analysis to check for risks.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {risks.map((risk, index) => (
              <div
                key={index}
                className="flex items-start gap-3 p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
              >
                <div className="mt-0.5">
                  {getSeverityIcon(risk.severity)}
                </div>
                <div className="flex-1 space-y-1">
                  <div className="flex items-center gap-2">
                    <Badge variant={getSeverityVariant(risk.severity)} className="text-xs">
                      {risk.severity}
                    </Badge>
                    {risk.category && (
                      <span className="text-xs text-muted-foreground">
                        {risk.category}
                      </span>
                    )}
                  </div>
                  <p className="text-sm">{risk.description || risk.risk || "Unknown risk"}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
