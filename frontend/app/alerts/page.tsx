/**
 * @file Alerts page — Business alert centre.
 */
"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Bell, AlertTriangle, AlertCircle, Info, Check } from "lucide-react";
import { useOrg } from "@/lib/org-context";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const severityConfig = {
  critical: { icon: AlertTriangle, color: "text-red-500", bg: "bg-red-50", border: "border-red-200" },
  warning: { icon: AlertCircle, color: "text-orange-500", bg: "bg-orange-50", border: "border-orange-200" },
  info: { icon: Info, color: "text-blue-500", bg: "bg-blue-50", border: "border-blue-200" },
};

export default function AlertsPage() {
  const { orgId } = useOrg();
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!orgId) return;
    setLoading(true);
    fetch(`${API}/api/alerts`, { headers: { "X-Org-ID": orgId } })
      .then((r) => (r.ok ? r.json() : []))
      .then(setAlerts)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [orgId]);

  const markRead = async (alertId: string) => {
    await fetch(`${API}/api/alerts/${alertId}/read`, {
      method: "PUT",
      headers: { "X-Org-ID": orgId },
    });
    setAlerts((prev) =>
      prev.map((a) => (a.alert_id === alertId ? { ...a, is_read: true } : a))
    );
  };

  const unread = alerts.filter((a) => !a.is_read);
  const read = alerts.filter((a) => a.is_read);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center gap-3 mb-6">
        <Bell className="h-6 w-6 text-primary" />
        <div>
          <h1 className="text-2xl font-bold">Alerts</h1>
          <p className="text-sm text-muted-foreground">
            {unread.length} unread alert{unread.length !== 1 ? "s" : ""}
          </p>
        </div>
      </div>

      {loading ? (
        <p className="text-sm text-muted-foreground py-8 text-center">Loading alerts...</p>
      ) : alerts.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Check className="h-10 w-10 text-green-500 mx-auto mb-3" />
            <p className="text-sm text-muted-foreground">No alerts right now. Your business is looking good.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {[...unread, ...read].map((alert: any) => {
            const config = severityConfig[alert.severity as keyof typeof severityConfig] || severityConfig.info;
            const Icon = config.icon;
            return (
              <Card
                key={alert.alert_id}
                className={`${alert.is_read ? "opacity-60" : ""} ${config.border}`}
              >
                <CardContent className="py-4">
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-lg ${config.bg}`}>
                      <Icon className={`h-4 w-4 ${config.color}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2">
                        <p className="font-medium text-sm">{alert.title}</p>
                        {!alert.is_read && (
                          <button
                            onClick={() => markRead(alert.alert_id)}
                            className="text-xs text-primary hover:underline shrink-0"
                          >
                            Mark read
                          </button>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mt-0.5">{alert.description}</p>
                      {alert.recommended_action && (
                        <p className="text-xs text-primary mt-1">→ {alert.recommended_action}</p>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
