/**
 * @file Invoices page (/invoices) — QuickBooks-style invoice management.
 * Create, list, send, record payments, and manage outbound invoices with email notifications.
 */
"use client";

import { useState, useEffect } from "react";
import { useOrg } from "@/lib/org-context";
import { listOutboundInvoices, createOutboundInvoice, updateInvoiceStatus, getInvoiceSummary, recordInvoicePayment, sendInvoiceReminder } from "@/lib/api";
import { FileText, Plus, Send, CheckCircle, XCircle, Copy, ExternalLink, Trash2, RefreshCw, Bell, DollarSign, Repeat } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

interface LineItem { description: string; quantity: number; unit_price: number; amount: number; }
interface Invoice {
  invoice_id: string; invoice_number: string; customer_name: string; customer_email?: string;
  total: string | number; amount_paid?: string | number; balance_due?: string | number;
  currency: string; status: string; due_date: string; issued_date: string;
  line_items: LineItem[]; is_recurring?: boolean;
}
interface Summary {
  total_invoices: number; total_invoiced: number; total_paid: number;
  total_outstanding: number; total_overdue: number; currency: string;
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-700", sent: "bg-blue-100 text-blue-700",
  viewed: "bg-yellow-100 text-yellow-700", paid: "bg-green-100 text-green-700",
  overdue: "bg-red-100 text-red-700", cancelled: "bg-gray-100 text-gray-400 line-through",
};

function formatCurrency(amount: number | string, currency = "NGN") {
  const num = typeof amount === "string" ? parseFloat(amount) : amount;
  if (isNaN(num)) return `${currency} 0.00`;
  if (currency === "NGN") return `\u20A6${num.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;
  return `${currency} ${num.toLocaleString("en-US", { minimumFractionDigits: 2 })}`;
}

export default function InvoicesPage() {
  const { orgId } = useOrg();
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  // Form state
  const [customerName, setCustomerName] = useState("");
  const [customerEmail, setCustomerEmail] = useState("");
  const [customerPhone, setCustomerPhone] = useState("");
  const [lineItems, setLineItems] = useState<{ description: string; quantity: number; unit_price: number }[]>([
    { description: "", quantity: 1, unit_price: 0 },
  ]);
  const [taxRate, setTaxRate] = useState(0);
  const [discount, setDiscount] = useState(0);
  const [notes, setNotes] = useState("");
  const [dueDays, setDueDays] = useState(30);
  const [isRecurring, setIsRecurring] = useState(false);
  const [recurrenceInterval, setRecurrenceInterval] = useState("monthly");

  // Partial payment modal state
  const [paymentModal, setPaymentModal] = useState<string | null>(null);
  const [paymentAmount, setPaymentAmount] = useState(0);
  const [paymentRef, setPaymentRef] = useState("");
  const [paymentMethod, setPaymentMethod] = useState("");
  const [recordingPayment, setRecordingPayment] = useState(false);

  useEffect(() => { if (orgId) loadData(); }, [orgId]);

  async function loadData() {
    setLoading(true); setError("");
    try {
      const [invRes, sumRes] = await Promise.all([
        listOutboundInvoices(orgId),
        getInvoiceSummary(orgId).catch(() => null),
      ]);
      setInvoices(invRes.invoices || []);
      if (sumRes) setSummary(sumRes);
    } catch (err: any) {
      const msg = err?.message || "";
      if (msg.includes("Failed to fetch") || msg.includes("timed out")) {
        setError("Could not reach the server. Please check that the backend is running and try again.");
      } else { setError(msg || "Something went wrong loading invoices."); }
    } finally { setLoading(false); }
  }

  function addLineItem() { setLineItems([...lineItems, { description: "", quantity: 1, unit_price: 0 }]); }
  function removeLineItem(idx: number) { setLineItems(lineItems.filter((_, i) => i !== idx)); }
  function updateLineItem(idx: number, field: string, value: string | number) {
    const updated = [...lineItems]; (updated[idx] as any)[field] = value; setLineItems(updated);
  }

  const subtotal = lineItems.reduce((sum, item) => sum + item.quantity * item.unit_price, 0);
  const taxAmount = subtotal * taxRate / 100;
  const total = subtotal + taxAmount - discount;

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!customerName.trim()) return;
    if (lineItems.some((li) => !li.description.trim() || li.unit_price <= 0)) {
      setError("All line items need a description and price"); return;
    }
    setCreating(true); setError("");
    try {
      await createOutboundInvoice(orgId, {
        customer_name: customerName, customer_email: customerEmail || undefined,
        customer_phone: customerPhone || undefined, line_items: lineItems,
        tax_rate: taxRate, discount, notes: notes || undefined, due_days: dueDays,
        is_recurring: isRecurring, recurrence_interval: isRecurring ? recurrenceInterval : undefined,
      } as any);
      setSuccessMsg("Invoice created"); setShowForm(false); resetForm(); loadData();
    } catch (err: any) { setError(err.message); }
    finally { setCreating(false); }
  }

  function resetForm() {
    setCustomerName(""); setCustomerEmail(""); setCustomerPhone("");
    setLineItems([{ description: "", quantity: 1, unit_price: 0 }]);
    setTaxRate(0); setDiscount(0); setNotes(""); setDueDays(30);
    setIsRecurring(false); setRecurrenceInterval("monthly");
  }

  async function handleStatusChange(invoiceId: string, status: string) {
    try {
      const res = await updateInvoiceStatus(orgId, invoiceId, status);
      if (res.email_sent) setSuccessMsg(`Invoice ${status} — email notification sent`);
      else setSuccessMsg(`Invoice marked as ${status}`);
      setTimeout(() => setSuccessMsg(""), 4000);
      loadData();
    } catch (err: any) { setError(err.message); }
  }

  async function handleRecordPayment() {
    if (!paymentModal || paymentAmount <= 0) return;
    setRecordingPayment(true);
    try {
      await recordInvoicePayment(orgId, paymentModal, {
        amount: paymentAmount, payment_reference: paymentRef || undefined,
        payment_method: paymentMethod || undefined,
      });
      setSuccessMsg("Payment recorded"); setPaymentModal(null);
      setPaymentAmount(0); setPaymentRef(""); setPaymentMethod("");
      setTimeout(() => setSuccessMsg(""), 4000); loadData();
    } catch (err: any) { setError(err.message); }
    finally { setRecordingPayment(false); }
  }

  async function handleSendReminder(invoiceId: string) {
    try {
      await sendInvoiceReminder(orgId, invoiceId);
      setSuccessMsg("Payment reminder sent"); setTimeout(() => setSuccessMsg(""), 4000);
    } catch (err: any) { setError(err.message); }
  }

  function copyPaymentLink(invoiceId: string) {
    const link = `${window.location.origin}/invoices/${invoiceId}`;
    navigator.clipboard.writeText(link);
    setSuccessMsg("Payment link copied"); setTimeout(() => setSuccessMsg(""), 3000);
  }

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileText className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-semibold">Invoices</h1>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={loadData}><RefreshCw className="h-4 w-4 mr-1" /> Refresh</Button>
          <Button size="sm" onClick={() => setShowForm(!showForm)}><Plus className="h-4 w-4 mr-1" /> New Invoice</Button>
        </div>
      </div>

      {successMsg && <div className="px-4 py-2 rounded-md bg-green-50 text-green-700 text-sm">{successMsg}</div>}
      {error && <div className="px-4 py-2 rounded-md bg-red-50 text-red-700 text-sm">{error}</div>}

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <Card><CardContent className="pt-4"><p className="text-xs text-muted-foreground">Total Invoiced</p><p className="text-lg font-semibold">{formatCurrency(summary.total_invoiced)}</p></CardContent></Card>
          <Card><CardContent className="pt-4"><p className="text-xs text-muted-foreground">Paid</p><p className="text-lg font-semibold text-green-600">{formatCurrency(summary.total_paid)}</p></CardContent></Card>
          <Card><CardContent className="pt-4"><p className="text-xs text-muted-foreground">Outstanding</p><p className="text-lg font-semibold text-blue-600">{formatCurrency(summary.total_outstanding)}</p></CardContent></Card>
          <Card><CardContent className="pt-4"><p className="text-xs text-muted-foreground">Overdue</p><p className="text-lg font-semibold text-red-600">{formatCurrency(summary.total_overdue)}</p></CardContent></Card>
          <Card><CardContent className="pt-4"><p className="text-xs text-muted-foreground">Invoices</p><p className="text-lg font-semibold">{summary.total_invoices}</p></CardContent></Card>
        </div>
      )}

      {/* Partial Payment Modal */}
      {paymentModal && (
        <Card className="border-2 border-primary/20">
          <CardHeader><h2 className="text-lg font-medium flex items-center gap-2"><DollarSign className="h-5 w-5" /> Record Payment</h2></CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="text-sm font-medium">Amount *</label>
                <input type="number" min={0.01} step={0.01} value={paymentAmount} onChange={(e) => setPaymentAmount(Number(e.target.value))}
                  className="w-full mt-1 rounded-md border px-3 py-2 text-sm" placeholder="0.00" />
              </div>
              <div>
                <label className="text-sm font-medium">Payment Method</label>
                <select value={paymentMethod} onChange={(e) => setPaymentMethod(e.target.value)}
                  className="w-full mt-1 rounded-md border px-3 py-2 text-sm">
                  <option value="">Select...</option>
                  <option value="bank_transfer">Bank Transfer</option>
                  <option value="cash">Cash</option>
                  <option value="paystack">Paystack</option>
                  <option value="flutterwave">Flutterwave</option>
                  <option value="mobile_money">Mobile Money</option>
                  <option value="ussd">USSD</option>
                  <option value="cheque">Cheque</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium">Reference</label>
                <input value={paymentRef} onChange={(e) => setPaymentRef(e.target.value)}
                  className="w-full mt-1 rounded-md border px-3 py-2 text-sm" placeholder="Transaction ref..." />
              </div>
              <div className="flex items-end gap-2">
                <Button onClick={handleRecordPayment} disabled={recordingPayment || paymentAmount <= 0}>
                  {recordingPayment ? "Recording..." : "Record Payment"}
                </Button>
                <Button variant="outline" onClick={() => setPaymentModal(null)}>Cancel</Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Create Invoice Form */}
      {showForm && (
        <Card>
          <CardHeader><h2 className="text-lg font-medium">Create New Invoice</h2></CardHeader>
          <CardContent>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium">Customer Name *</label>
                  <input value={customerName} onChange={(e) => setCustomerName(e.target.value)} required
                    className="w-full mt-1 rounded-md border px-3 py-2 text-sm" placeholder="Customer or business name" />
                </div>
                <div>
                  <label className="text-sm font-medium">Email</label>
                  <input type="email" value={customerEmail} onChange={(e) => setCustomerEmail(e.target.value)}
                    className="w-full mt-1 rounded-md border px-3 py-2 text-sm" placeholder="customer@email.com" />
                </div>
                <div>
                  <label className="text-sm font-medium">Phone</label>
                  <input value={customerPhone} onChange={(e) => setCustomerPhone(e.target.value)}
                    className="w-full mt-1 rounded-md border px-3 py-2 text-sm" placeholder="+234..." />
                </div>
              </div>

              {/* Line Items */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium">Line Items</label>
                  <button type="button" onClick={addLineItem} className="text-xs text-primary hover:underline">+ Add item</button>
                </div>
                <div className="space-y-2">
                  {lineItems.map((item, idx) => (
                    <div key={idx} className="grid grid-cols-12 gap-2 items-end">
                      <div className="col-span-5">
                        {idx === 0 && <span className="text-xs text-muted-foreground">Description</span>}
                        <input value={item.description} onChange={(e) => updateLineItem(idx, "description", e.target.value)}
                          className="w-full rounded-md border px-3 py-2 text-sm" placeholder="Item description" required />
                      </div>
                      <div className="col-span-2">
                        {idx === 0 && <span className="text-xs text-muted-foreground">Qty</span>}
                        <input type="number" min={1} value={item.quantity} onChange={(e) => updateLineItem(idx, "quantity", Number(e.target.value))}
                          className="w-full rounded-md border px-3 py-2 text-sm" />
                      </div>
                      <div className="col-span-3">
                        {idx === 0 && <span className="text-xs text-muted-foreground">Unit Price</span>}
                        <input type="number" min={0} step={0.01} value={item.unit_price} onChange={(e) => updateLineItem(idx, "unit_price", Number(e.target.value))}
                          className="w-full rounded-md border px-3 py-2 text-sm" />
                      </div>
                      <div className="col-span-1 text-right text-sm font-medium py-2">{formatCurrency(item.quantity * item.unit_price)}</div>
                      <div className="col-span-1">
                        {lineItems.length > 1 && (
                          <button type="button" onClick={() => removeLineItem(idx)} className="p-2 text-red-500 hover:text-red-700"><Trash2 className="h-4 w-4" /></button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Totals + Recurring */}
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <div>
                  <label className="text-sm font-medium">Tax Rate (%)</label>
                  <input type="number" min={0} max={100} step={0.5} value={taxRate} onChange={(e) => setTaxRate(Number(e.target.value))}
                    className="w-full mt-1 rounded-md border px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="text-sm font-medium">Discount</label>
                  <input type="number" min={0} step={0.01} value={discount} onChange={(e) => setDiscount(Number(e.target.value))}
                    className="w-full mt-1 rounded-md border px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="text-sm font-medium">Due (days)</label>
                  <input type="number" min={1} max={365} value={dueDays} onChange={(e) => setDueDays(Number(e.target.value))}
                    className="w-full mt-1 rounded-md border px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="text-sm font-medium flex items-center gap-1"><Repeat className="h-3.5 w-3.5" /> Recurring</label>
                  <div className="flex items-center gap-2 mt-1">
                    <input type="checkbox" checked={isRecurring} onChange={(e) => setIsRecurring(e.target.checked)} className="rounded" />
                    {isRecurring && (
                      <select value={recurrenceInterval} onChange={(e) => setRecurrenceInterval(e.target.value)}
                        className="rounded-md border px-2 py-1.5 text-sm flex-1">
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                        <option value="quarterly">Quarterly</option>
                        <option value="yearly">Yearly</option>
                      </select>
                    )}
                  </div>
                </div>
                <div className="flex flex-col justify-end">
                  <p className="text-xs text-muted-foreground">Subtotal: {formatCurrency(subtotal)}</p>
                  {taxRate > 0 && <p className="text-xs text-muted-foreground">Tax: {formatCurrency(taxAmount)}</p>}
                  {discount > 0 && <p className="text-xs text-muted-foreground">Discount: -{formatCurrency(discount)}</p>}
                  <p className="text-sm font-semibold">Total: {formatCurrency(total)}</p>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium">Notes</label>
                <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={2}
                  className="w-full mt-1 rounded-md border px-3 py-2 text-sm" placeholder="Payment terms, bank details, thank you note..." />
              </div>

              <div className="flex gap-2">
                <Button type="submit" disabled={creating}>{creating ? "Creating..." : "Create Invoice"}</Button>
                <Button type="button" variant="outline" onClick={() => { setShowForm(false); resetForm(); }}>Cancel</Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Invoice List */}
      {loading ? (
        <div className="text-center py-12 text-muted-foreground">Loading invoices...</div>
      ) : invoices.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <FileText className="h-12 w-12 mx-auto text-muted-foreground/30 mb-4" />
            <p className="text-muted-foreground">No invoices yet. Create your first invoice to get started.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="border rounded-lg overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left px-4 py-3 font-medium">Invoice #</th>
                <th className="text-left px-4 py-3 font-medium">Customer</th>
                <th className="text-left px-4 py-3 font-medium">Amount</th>
                <th className="text-left px-4 py-3 font-medium">Paid</th>
                <th className="text-left px-4 py-3 font-medium">Status</th>
                <th className="text-left px-4 py-3 font-medium">Due Date</th>
                <th className="text-left px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {invoices.map((inv) => {
                const amtPaid = parseFloat(String(inv.amount_paid || 0));
                const invTotal = parseFloat(String(inv.total || 0));
                const hasPartial = amtPaid > 0 && amtPaid < invTotal;
                return (
                <tr key={inv.invoice_id} className="hover:bg-muted/30">
                  <td className="px-4 py-3 font-medium">
                    {inv.invoice_number}
                    {inv.is_recurring && <Repeat className="inline h-3 w-3 ml-1 text-primary" title="Recurring" />}
                  </td>
                  <td className="px-4 py-3">
                    <p>{inv.customer_name}</p>
                    {inv.customer_email && <p className="text-xs text-muted-foreground">{inv.customer_email}</p>}
                  </td>
                  <td className="px-4 py-3 font-medium">{formatCurrency(inv.total, inv.currency)}</td>
                  <td className="px-4 py-3">
                    {amtPaid > 0 ? (
                      <span className={hasPartial ? "text-yellow-600" : "text-green-600"}>
                        {formatCurrency(amtPaid, inv.currency)}
                      </span>
                    ) : <span className="text-muted-foreground">—</span>}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_COLORS[inv.status] || "bg-gray-100"}`}>
                      {inv.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">{inv.due_date}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      {inv.status === "draft" && (
                        <button onClick={() => handleStatusChange(inv.invoice_id, "sent")}
                          className="p-1.5 rounded hover:bg-accent text-blue-600" title="Send Invoice (email)">
                          <Send className="h-3.5 w-3.5" />
                        </button>
                      )}
                      {inv.status !== "paid" && inv.status !== "cancelled" && (
                        <button onClick={() => { setPaymentModal(inv.invoice_id); setPaymentAmount(0); }}
                          className="p-1.5 rounded hover:bg-accent text-green-600" title="Record Payment">
                          <DollarSign className="h-3.5 w-3.5" />
                        </button>
                      )}
                      {(inv.status === "sent" || inv.status === "viewed" || inv.status === "overdue") && (
                        <button onClick={() => handleSendReminder(inv.invoice_id)}
                          className="p-1.5 rounded hover:bg-accent text-orange-500" title="Send Reminder">
                          <Bell className="h-3.5 w-3.5" />
                        </button>
                      )}
                      {(inv.status === "sent" || inv.status === "viewed") && (
                        <button onClick={() => handleStatusChange(inv.invoice_id, "paid")}
                          className="p-1.5 rounded hover:bg-accent text-green-600" title="Mark Fully Paid">
                          <CheckCircle className="h-3.5 w-3.5" />
                        </button>
                      )}
                      {inv.status !== "cancelled" && inv.status !== "paid" && (
                        <button onClick={() => handleStatusChange(inv.invoice_id, "cancelled")}
                          className="p-1.5 rounded hover:bg-accent text-red-500" title="Cancel">
                          <XCircle className="h-3.5 w-3.5" />
                        </button>
                      )}
                      <button onClick={() => copyPaymentLink(inv.invoice_id)}
                        className="p-1.5 rounded hover:bg-accent text-muted-foreground" title="Copy Payment Link">
                        <Copy className="h-3.5 w-3.5" />
                      </button>
                      <a href={`/invoices/${inv.invoice_id}`} target="_blank" rel="noopener noreferrer"
                        className="p-1.5 rounded hover:bg-accent text-muted-foreground" title="View Invoice">
                        <ExternalLink className="h-3.5 w-3.5" />
                      </a>
                    </div>
                  </td>
                </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
