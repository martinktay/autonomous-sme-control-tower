/**
 * @file Transactions page — list transactions with filters, summary, and cashflow view.
 * Mobile-first layout with practical language for African SME owners.
 */
"use client";

import { useEffect, useState } from "react";
import {
  getTransactions,
  getTransactionSummary,
  createTransaction,
} from "@/lib/api";
import CurrencyDisplay from "@/components/CurrencyDisplay";
import {
  ArrowDownCircle,
  ArrowUpCircle,
  Plus,
  Filter,
  Loader2,
} from "lucide-react";
import { useOrg } from "@/lib/org-context";
import { formatDate } from "@/lib/format-date";

interface Transaction {
  transaction_id: string;
  description: string;
  amount: number;
  currency: string;
  transaction_type: string;
  category: string | null;
  counterparty_name: string | null;
  payment_status: string;
  date: string;
}

interface Summary {
  total_revenue: number;
  total_expenses: number;
  net: number;
  count: number;
}

const typeConfig: Record<string, { icon: typeof ArrowUpCircle; color: string }> = {
  revenue: { icon: ArrowDownCircle, color: "text-green-600" },
  expense: { icon: ArrowUpCircle, color: "text-red-500" },
  payment: { icon: ArrowUpCircle, color: "text-orange-500" },
  transfer: { icon: ArrowDownCircle, color: "text-blue-500" },
};

export default function TransactionsPage() {
  const { orgId } = useOrg();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<string>("all");
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    if (!orgId) return;
    setLoading(true);
    Promise.all([
      getTransactions(orgId).then((r) => r.json()),
      getTransactionSummary(orgId).then((r) => r.json()),
    ])
      .then(([txns, sum]) => {
        setTransactions(Array.isArray(txns) ? txns : []);
        setSummary(sum && typeof sum === "object" ? sum : null);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [orgId]);

  const filtered =
    filterType === "all"
      ? transactions
      : transactions.filter((t) => t.transaction_type === filterType);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Transactions</h1>
          <p className="text-sm text-muted-foreground">
            Track money in and out of your business
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-1.5 bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium hover:opacity-90"
        >
          <Plus className="h-4 w-4" /> Add
        </button>
      </div>

      {/* Summary cards */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          <SummaryCard label="Revenue" value={summary.total_revenue} color="text-green-600" />
          <SummaryCard label="Expenses" value={summary.total_expenses} color="text-red-500" />
          <SummaryCard label="Net" value={summary.net} color={summary.net >= 0 ? "text-green-600" : "text-red-500"} />
          <div className="bg-card border rounded-lg p-3">
            <p className="text-xs text-muted-foreground">Transactions</p>
            <p className="text-lg font-semibold">{summary.count}</p>
          </div>
        </div>
      )}

      {/* Quick add form */}
      {showForm && <QuickAddForm orgId={orgId} onCreated={(t) => { setTransactions((prev) => [t, ...prev]); setShowForm(false); }} />}

      {/* Filter bar */}
      <div className="flex items-center gap-2 mb-4 overflow-x-auto pb-1">
        <Filter className="h-4 w-4 text-muted-foreground shrink-0" />
        {["all", "revenue", "expense", "payment", "transfer"].map((t) => (
          <button
            key={t}
            onClick={() => setFilterType(t)}
            className={`px-3 py-1 rounded-full text-xs font-medium capitalize whitespace-nowrap ${
              filterType === t ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground hover:bg-muted/80"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Transaction list */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-12 text-sm text-muted-foreground">
          No transactions yet. Upload data or add one manually.
        </div>
      ) : (
        <div className="space-y-2">
          {filtered.map((txn) => {
            const cfg = typeConfig[txn.transaction_type] || typeConfig.expense;
            const Icon = cfg.icon;
            return (
              <div key={txn.transaction_id} className="flex items-center gap-3 bg-card border rounded-lg p-3">
                <Icon className={`h-5 w-5 shrink-0 ${cfg.color}`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{txn.description || txn.counterparty_name || "Transaction"}</p>
                  <p className="text-xs text-muted-foreground">
                    {txn.category && <span className="mr-2">{txn.category}</span>}
                    {formatDate(txn.date)}
                    <span className={`ml-2 px-1.5 py-0.5 rounded text-[10px] font-medium ${
                      txn.payment_status === "paid" ? "bg-green-100 text-green-700" :
                      txn.payment_status === "overdue" ? "bg-red-100 text-red-700" :
                      "bg-yellow-100 text-yellow-700"
                    }`}>{txn.payment_status}</span>
                  </p>
                </div>
                <CurrencyDisplay
                  amount={txn.transaction_type === "expense" ? -txn.amount : txn.amount}
                  currency={(txn.currency || "NGN") as any}
                  className="text-sm font-semibold"
                />
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function SummaryCard({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="bg-card border rounded-lg p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <CurrencyDisplay amount={value} className={`text-lg font-semibold ${color}`} />
    </div>
  );
}

function QuickAddForm({ orgId, onCreated }: { orgId: string; onCreated: (t: Transaction) => void }) {
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    description: "",
    amount: "",
    transaction_type: "expense",
    date: new Date().toISOString().slice(0, 10),
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.description || !form.amount) return;
    setSaving(true);
    try {
      const res = await createTransaction(orgId, {
        description: form.description,
        amount: parseFloat(form.amount),
        transaction_type: form.transaction_type,
        date: new Date(form.date).toISOString(),
        payment_status: "paid",
      });
      if (res) {
        const result = await res.json();
        onCreated(result as Transaction);
      }
    } catch {
      /* swallow */
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-card border rounded-lg p-4 mb-4 space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <input
          placeholder="Description"
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
          className="col-span-2 border rounded-lg px-3 py-2 text-sm bg-background"
          required
        />
        <input
          type="number"
          placeholder="Amount"
          value={form.amount}
          onChange={(e) => setForm({ ...form, amount: e.target.value })}
          className="border rounded-lg px-3 py-2 text-sm bg-background"
          min="0.01"
          step="0.01"
          required
        />
        <select
          value={form.transaction_type}
          onChange={(e) => setForm({ ...form, transaction_type: e.target.value })}
          className="border rounded-lg px-3 py-2 text-sm bg-background"
        >
          <option value="revenue">Revenue</option>
          <option value="expense">Expense</option>
          <option value="payment">Payment</option>
          <option value="transfer">Transfer</option>
        </select>
        <input
          type="date"
          value={form.date}
          onChange={(e) => setForm({ ...form, date: e.target.value })}
          className="border rounded-lg px-3 py-2 text-sm bg-background"
        />
        <button
          type="submit"
          disabled={saving}
          className="bg-primary text-primary-foreground rounded-lg px-4 py-2 text-sm font-medium hover:opacity-90 disabled:opacity-50"
        >
          {saving ? "Saving..." : "Save"}
        </button>
      </div>
    </form>
  );
}
