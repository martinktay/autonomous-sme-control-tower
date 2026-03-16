/**
 * ActionLog — Renders a chronological list of autonomous actions
 * executed by the control-tower orchestration loop.
 * Each entry shows status icon, badge, target entity, and timestamp.
 */
"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, XCircle, Clock, Play, Loader2, Inbox } from "lucide-react";

interface Action {
  execution_id: string;
  action_type: string;
  target_entity: string;
  execution_status: string;
  timestamp: string;
  error_reason?: string;
}

interface ActionLogProps {
  actions: Action[];
  loading?: boolean;
}

export default function ActionLog({ actions, loading }: ActionLogProps) {
  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case "success":
        return <CheckCircle2 className="h-4 w-4 text-green-600" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-600" />;
      case "pending":
        return <Clock className="h-4 w-4 text-yellow-600" />;
      default:
        return <Play className="h-4 w-4 text-blue-600" />;
    }
  };

  const getStatusVariant = (status: string): "default" | "secondary" | "destructive" | "outline" => {
    switch (status.toLowerCase()) {
      case "success":
        return "default";
      case "failed":
        return "destructive";
      case "pending":
        return "secondary";
      default:
        return "outline";
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Action History</CardTitle>
        <CardDescription>
          Things the AI has done for your business automatically — like chasing payments or flagging risks. Green means it worked, red means it hit a problem.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center gap-2 text-muted-foreground py-4">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">Loading actions…</span>
          </div>
        ) : actions.length === 0 ? (
          <div className="flex flex-col items-center py-6 text-center">
            <Inbox className="h-8 w-8 text-muted-foreground mb-2" />
            <p className="text-sm font-medium">No actions yet</p>
            <p className="text-xs text-muted-foreground mt-1">Actions will appear here after you run an analysis.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {[...actions]
              .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
              .map((action) => (
              <div
                key={action.execution_id}
                className="flex items-start gap-3 p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
              >
                <div className="mt-0.5">
                  {getStatusIcon(action.execution_status)}
                </div>
                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant={getStatusVariant(action.execution_status)} className="text-xs">
                        {action.execution_status}
                      </Badge>
                      <span className="text-sm font-medium">{action.action_type}</span>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {formatTimestamp(action.timestamp)}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Target: {action.target_entity}
                  </p>
                  {action.error_reason && (
                    <p className="text-xs text-red-600 mt-1">
                      Error: {action.error_reason}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
