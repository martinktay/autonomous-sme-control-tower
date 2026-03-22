/**
 * @file Suppliers & Customers page — Counterparty management.
 */
"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Users, Plus, ArrowUpRight, ArrowDownRight } from "lucide-react";
import { useOrg } from "@/lib/org-context";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function SuppliersPage() {
  const { orgId } = useOrg();
  const [counterparties, setCounterparties] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!orgId) return;
    setLoading(true);
    fetch(`${API}/api/counterparties`, { headers: { "X-Org-ID": orgId } })
      .then((r) => (r.ok ? r.json() : []))
      .then(setCounterparties)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [orgId]);

  const suppliers = counterparties.filter((c) => c.counterparty_type === "supplier");
  const customers = counterparties.filter((c) => c.counterparty_type === "customer");
  const totalOwed = suppliers.reduce((s, c) => s + Number(c.balance_owed || 0), 0);
  const totalOwing = customers.reduce((s, c) => s + Number(c.balance_owing || 0), 0);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Suppliers & Customers</h1>
          <p className="text-sm text-muted-foreground">Track who you owe and who owes you</p>
        </div>
        <Button className="gap-1">
          <Plus className="h-4 w-4" /> Add
        </Button>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Users className="h-8 w-8 text-primary" />
              <div>
                <p className="text-2xl font-bold">{counterparties.length}</p>
                <p className="text-xs text-muted-foreground">Total Contacts</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <ArrowUpRight className="h-8 w-8 text-red-500" />
              <div>
                <p className="text-2xl font-bold">₦{totalOwed.toLocaleString()}</p>
                <p className="text-xs text-muted-foreground">You Owe (Suppliers)</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <ArrowDownRight className="h-8 w-8 text-green-500" />
              <div>
                <p className="text-2xl font-bold">₦{totalOwing.toLocaleString()}</p>
                <p className="text-xs text-muted-foreground">Owed to You (Customers)</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Suppliers */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-base">Suppliers ({suppliers.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-sm text-muted-foreground py-4 text-center">Loading...</p>
          ) : suppliers.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4 text-center">No suppliers yet.</p>
          ) : (
            <div className="space-y-2">
              {suppliers.map((s: any) => (
                <div key={s.counterparty_id} className="flex items-center justify-between p-3 rounded-lg border">
                  <div>
                    <p className="font-medium text-sm">{s.name}</p>
                    <p className="text-xs text-muted-foreground">{s.phone || s.email || "No contact"}</p>
                  </div>
                  <p className="text-sm font-medium text-red-600">
                    ₦{Number(s.balance_owed || 0).toLocaleString()} owed
                  </p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Customers */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Customers ({customers.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-sm text-muted-foreground py-4 text-center">Loading...</p>
          ) : customers.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4 text-center">No customers yet.</p>
          ) : (
            <div className="space-y-2">
              {customers.map((c: any) => (
                <div key={c.counterparty_id} className="flex items-center justify-between p-3 rounded-lg border">
                  <div>
                    <p className="font-medium text-sm">{c.name}</p>
                    <p className="text-xs text-muted-foreground">{c.phone || c.email || "No contact"}</p>
                  </div>
                  <p className="text-sm font-medium text-green-600">
                    ₦{Number(c.balance_owing || 0).toLocaleString()} owing
                  </p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
