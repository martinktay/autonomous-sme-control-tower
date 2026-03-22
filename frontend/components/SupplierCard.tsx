/**
 * @file SupplierCard — Supplier/customer balance summary card.
 * Shows counterparty name, type, contact info, and outstanding balance.
 */
"use client";

import { Building2, Phone, Mail } from "lucide-react";
import CurrencyDisplay from "@/components/CurrencyDisplay";

interface SupplierCardProps {
  name: string;
  counterparty_type: "supplier" | "customer" | "both";
  phone?: string;
  email?: string;
  outstanding_balance?: number;
  total_transactions?: number;
  currency?: "NGN" | "USD" | "GBP" | "EUR";
}

const TYPE_LABELS: Record<string, string> = {
  supplier: "Supplier",
  customer: "Customer",
  both: "Supplier & Customer",
};

export default function SupplierCard({
  name,
  counterparty_type,
  phone,
  email,
  outstanding_balance = 0,
  total_transactions = 0,
  currency = "NGN",
}: SupplierCardProps) {
  return (
    <div className="rounded-lg border bg-card p-4 hover:shadow-sm transition-shadow">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10">
            <Building2 className="h-5 w-5 text-primary" />
          </div>
          <div className="min-w-0">
            <h3 className="font-medium truncate">{name}</h3>
            <p className="text-xs text-muted-foreground">{TYPE_LABELS[counterparty_type] || counterparty_type}</p>
          </div>
        </div>
        <div className="text-right shrink-0">
          <div className="text-xs text-muted-foreground">Balance</div>
          <CurrencyDisplay
            amount={outstanding_balance}
            currency={currency}
            className="font-semibold text-sm"
          />
        </div>
      </div>

      <div className="mt-3 flex items-center gap-4 text-xs text-muted-foreground">
        {phone && (
          <span className="flex items-center gap-1">
            <Phone className="h-3 w-3" /> {phone}
          </span>
        )}
        {email && (
          <span className="flex items-center gap-1 truncate">
            <Mail className="h-3 w-3" /> {email}
          </span>
        )}
        {total_transactions > 0 && (
          <span>{total_transactions} transactions</span>
        )}
      </div>
    </div>
  );
}
