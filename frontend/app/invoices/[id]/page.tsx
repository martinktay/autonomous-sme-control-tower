/**
 * @file Invoice detail page (/invoices/[id]) — Public invoice view with print and PDF download.
 * Shareable payment link for customers, no auth required.
 */
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getPublicInvoice } from "@/lib/api";
import { Building2, FileText, CheckCircle, Printer, Download, CreditCard } from "lucide-react";
import { Button } from "@/components/ui/button";

interface LineItem { description: string; quantity: number; unit_price: number; amount: number; }
interface PaymentRecord { amount: string; recorded_at: string; payment_method: string; }
interface PublicInvoice {
  invoice_id: string; invoice_number: string; business_name: string;
  business_email: string; business_phone: string; customer_name: string;
  line_items: LineItem[]; subtotal: string | number; tax_rate: string | number;
  tax_amount: string | number; discount: string | number; total: string | number;
  amount_paid: string | number; balance_due: string | number;
  currency: string; status: string; due_date: string; issued_date: string;
  notes: string; payments: PaymentRecord[];
}

function fmt(amount: number | string, currency = "NGN") {
  const num = typeof amount === "string" ? parseFloat(amount) : amount;
  if (isNaN(num)) return `${currency} 0.00`;
  if (currency === "NGN") return `\u20A6${num.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;
  return `${currency} ${num.toLocaleString("en-US", { minimumFractionDigits: 2 })}`;
}

export default function PublicInvoicePage() {
  const params = useParams();
  const invoiceId = params.id as string;
  const [invoice, setInvoice] = useState<PublicInvoice | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!invoiceId) return;
    getPublicInvoice(invoiceId)
      .then((data) => setInvoice(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [invoiceId]);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-muted-foreground">Loading invoice...</p>
    </div>
  );

  if (error || !invoice) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center space-y-2">
        <FileText className="h-12 w-12 mx-auto text-muted-foreground/30" />
        <p className="text-muted-foreground">Invoice not found or has been removed.</p>
      </div>
    </div>
  );

  const isPaid = invoice.status === "paid";
  const balanceDue = parseFloat(String(invoice.balance_due || invoice.total || 0));
  const amountPaid = parseFloat(String(invoice.amount_paid || 0));
  const hasPartialPayment = amountPaid > 0 && !isPaid;

  function handlePrint() { window.print(); }
  function handleDownloadPdf() { window.print(); }

  function handlePayWithPaystack() {
    // Paystack inline popup — loads their JS SDK
    const paystackKey = process.env.NEXT_PUBLIC_PAYSTACK_PUBLIC_KEY;
    if (!paystackKey) {
      alert("Online payment is not configured yet. Please contact the business directly to arrange payment.");
      return;
    }
    const script = document.createElement("script");
    script.src = "https://js.paystack.co/v1/inline.js";
    script.onload = () => {
      const handler = (window as any).PaystackPop.setup({
        key: paystackKey,
        email: invoice?.business_email || "customer@example.com",
        amount: Math.round(balanceDue * 100), // Paystack uses kobo
        currency: invoice?.currency || "NGN",
        ref: `INV-${invoiceId}-${Date.now()}`,
        metadata: { invoice_id: invoiceId, invoice_number: invoice?.invoice_number },
        callback: () => { alert("Payment successful! The business will be notified."); window.location.reload(); },
        onClose: () => {},
      });
      handler.openIframe();
    };
    document.body.appendChild(script);
  }

  function handlePayWithFlutterwave() {
    const flwKey = process.env.NEXT_PUBLIC_FLUTTERWAVE_PUBLIC_KEY;
    if (!flwKey) {
      alert("Online payment is not configured yet. Please contact the business directly to arrange payment.");
      return;
    }
    const script = document.createElement("script");
    script.src = "https://checkout.flutterwave.com/v3.js";
    script.onload = () => {
      (window as any).FlutterwaveCheckout({
        public_key: flwKey,
        tx_ref: `INV-${invoiceId}-${Date.now()}`,
        amount: balanceDue,
        currency: invoice?.currency || "NGN",
        payment_options: "card,banktransfer,ussd,mobilemoney",
        customer: { email: invoice?.business_email || "customer@example.com", name: invoice?.customer_name },
        customizations: { title: `Invoice ${invoice?.invoice_number}`, description: `Payment for invoice ${invoice?.invoice_number}` },
        callback: () => { alert("Payment successful! The business will be notified."); window.location.reload(); },
        onclose: () => {},
      });
    };
    document.body.appendChild(script);
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      {/* Action bar */}
      <div className="max-w-3xl mx-auto mb-4 flex justify-end gap-2 print:hidden">
        <Button variant="outline" size="sm" onClick={handlePrint} className="gap-1.5">
          <Printer className="h-4 w-4" /> Print Receipt
        </Button>
        <Button variant="outline" size="sm" onClick={handleDownloadPdf} className="gap-1.5">
          <Download className="h-4 w-4" /> Save as PDF
        </Button>
      </div>

      <div className="max-w-3xl mx-auto bg-white rounded-lg shadow-sm border print:shadow-none print:border-0">
        {/* Header */}
        <div className="p-8 border-b">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Building2 className="h-5 w-5 text-primary" />
                <h1 className="text-xl font-semibold">{invoice.business_name || "SME Control Tower"}</h1>
              </div>
              {invoice.business_email && <p className="text-sm text-muted-foreground">{invoice.business_email}</p>}
              {invoice.business_phone && <p className="text-sm text-muted-foreground">{invoice.business_phone}</p>}
            </div>
            <div className="text-right">
              <h2 className="text-2xl font-semibold text-primary">INVOICE</h2>
              <p className="text-sm text-muted-foreground">{invoice.invoice_number}</p>
              {isPaid && (
                <div className="mt-2 flex items-center gap-1 justify-end text-green-600">
                  <CheckCircle className="h-4 w-4" /><span className="text-sm font-medium">PAID</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Bill To + Dates */}
        <div className="p-8 grid grid-cols-2 gap-8 border-b">
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase mb-1">Bill To</p>
            <p className="font-medium">{invoice.customer_name}</p>
          </div>
          <div className="text-right space-y-1">
            <div><span className="text-xs text-muted-foreground">Issued: </span><span className="text-sm">{invoice.issued_date}</span></div>
            <div><span className="text-xs text-muted-foreground">Due: </span><span className="text-sm font-medium">{invoice.due_date}</span></div>
          </div>
        </div>

        {/* Line Items */}
        <div className="p-8">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 font-medium">Description</th>
                <th className="text-right py-2 font-medium w-20">Qty</th>
                <th className="text-right py-2 font-medium w-28">Unit Price</th>
                <th className="text-right py-2 font-medium w-28">Amount</th>
              </tr>
            </thead>
            <tbody>
              {(invoice.line_items || []).map((item, idx) => (
                <tr key={idx} className="border-b border-dashed">
                  <td className="py-2">{item.description}</td>
                  <td className="py-2 text-right">{item.quantity}</td>
                  <td className="py-2 text-right">{fmt(item.unit_price, invoice.currency)}</td>
                  <td className="py-2 text-right">{fmt(item.amount || item.quantity * item.unit_price, invoice.currency)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Totals */}
          <div className="mt-6 flex justify-end">
            <div className="w-64 space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Subtotal</span>
                <span>{fmt(invoice.subtotal, invoice.currency)}</span>
              </div>
              {parseFloat(String(invoice.tax_rate)) > 0 && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Tax ({invoice.tax_rate}%)</span>
                  <span>{fmt(invoice.tax_amount, invoice.currency)}</span>
                </div>
              )}
              {parseFloat(String(invoice.discount)) > 0 && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Discount</span>
                  <span>-{fmt(invoice.discount, invoice.currency)}</span>
                </div>
              )}
              <div className="flex justify-between text-base font-semibold border-t pt-2 mt-2">
                <span>Total</span>
                <span>{fmt(invoice.total, invoice.currency)}</span>
              </div>
              {hasPartialPayment && (
                <>
                  <div className="flex justify-between text-sm text-green-600">
                    <span>Amount Paid</span>
                    <span>-{fmt(amountPaid, invoice.currency)}</span>
                  </div>
                  <div className="flex justify-between text-base font-semibold text-primary">
                    <span>Balance Due</span>
                    <span>{fmt(balanceDue, invoice.currency)}</span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Payment History */}
        {invoice.payments && invoice.payments.length > 0 && (
          <div className="px-8 pb-4">
            <p className="text-xs font-medium text-muted-foreground uppercase mb-2">Payment History</p>
            <div className="space-y-1">
              {invoice.payments.map((p, idx) => (
                <div key={idx} className="flex justify-between text-sm bg-green-50 rounded px-3 py-1.5">
                  <span className="text-green-700">{fmt(p.amount, invoice.currency)} — {p.payment_method || "Payment"}</span>
                  <span className="text-muted-foreground text-xs">{p.recorded_at?.slice(0, 10)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Notes */}
        {invoice.notes && (
          <div className="px-8 pb-8">
            <p className="text-xs font-medium text-muted-foreground uppercase mb-1">Notes</p>
            <p className="text-sm text-muted-foreground whitespace-pre-wrap">{invoice.notes}</p>
          </div>
        )}

        {/* Pay Now Section — only shown if not paid */}
        {!isPaid && (
          <div className="p-8 border-t bg-blue-50/50 print:hidden">
            <div className="text-center space-y-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Amount Due</p>
                <p className="text-3xl font-bold text-primary">{fmt(balanceDue, invoice.currency)}</p>
                {hasPartialPayment && <p className="text-xs text-muted-foreground">Partial payment of {fmt(amountPaid, invoice.currency)} received</p>}
              </div>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Button onClick={handlePayWithPaystack} className="gap-2 bg-green-600 hover:bg-green-700">
                  <CreditCard className="h-4 w-4" /> Pay with Paystack
                </Button>
                <Button onClick={handlePayWithFlutterwave} variant="outline" className="gap-2 border-orange-300 text-orange-600 hover:bg-orange-50">
                  <CreditCard className="h-4 w-4" /> Pay with Flutterwave
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                Supports card, bank transfer, USSD, and mobile money
              </p>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="p-6 bg-muted/30 rounded-b-lg text-center print:bg-white">
          <p className="text-xs text-muted-foreground">
            {isPaid ? "RECEIPT — Payment Confirmed" : "INVOICE"} &mdash; Generated by SME Control Tower
          </p>
          <p className="text-xs text-muted-foreground mt-1 print:hidden">
            Use the Print or Save as PDF buttons above to get a hard or soft copy.
          </p>
        </div>
      </div>
    </div>
  );
}
