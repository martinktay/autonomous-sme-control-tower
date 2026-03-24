"""
Notification service — centralised email notifications via SES.

Handles all transactional emails: welcome, invoice delivery, payment
confirmation, overdue reminders, and general platform notifications.
Uses HTML templates with Africa-native, practical language.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from app.services.ses_service import get_ses_service
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# ── Shared HTML wrapper ──────────────────────────────────────────────────

_BASE_STYLE = """
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f4f4f5; }
  .container { max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; }
  .header { background: #1e293b; color: #ffffff; padding: 24px 32px; }
  .header h1 { margin: 0; font-size: 20px; font-weight: 600; }
  .header p { margin: 4px 0 0; font-size: 13px; color: #94a3b8; }
  .body { padding: 32px; color: #334155; line-height: 1.6; }
  .body h2 { margin: 0 0 16px; font-size: 18px; color: #1e293b; }
  .body p { margin: 0 0 12px; font-size: 14px; }
  .btn { display: inline-block; padding: 12px 28px; background: #2563eb; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 14px; }
  .btn-green { background: #16a34a; }
  .footer { padding: 20px 32px; background: #f8fafc; text-align: center; font-size: 12px; color: #94a3b8; }
  .table { width: 100%; border-collapse: collapse; margin: 16px 0; }
  .table th { text-align: left; padding: 8px 12px; background: #f1f5f9; font-size: 12px; color: #64748b; border-bottom: 1px solid #e2e8f0; }
  .table td { padding: 8px 12px; font-size: 13px; border-bottom: 1px solid #f1f5f9; }
  .total-row td { font-weight: 600; font-size: 15px; border-top: 2px solid #1e293b; }
  .badge { display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }
  .badge-paid { background: #dcfce7; color: #166534; }
  .badge-due { background: #fef3c7; color: #92400e; }
  .badge-overdue { background: #fee2e2; color: #991b1b; }
</style>
"""


def _wrap_html(content: str) -> str:
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">{_BASE_STYLE}</head><body>
<div style="padding:20px 0"><div class="container">{content}</div></div>
</body></html>"""


def _header(title: str, subtitle: str = "") -> str:
    sub = f'<p>{subtitle}</p>' if subtitle else ''
    return f'<div class="header"><h1>{title}</h1>{sub}</div>'


def _footer() -> str:
    return '<div class="footer">Powered by SME Control Tower &mdash; Your AI Business Assistant</div>'


# ── Format helpers ───────────────────────────────────────────────────────

def _fmt_currency(amount, currency="NGN") -> str:
    try:
        num = float(amount)
    except (TypeError, ValueError):
        return str(amount)
    if currency == "NGN":
        return f"₦{num:,.2f}"
    if currency == "USD":
        return f"${num:,.2f}"
    if currency == "GBP":
        return f"£{num:,.2f}"
    if currency == "EUR":
        return f"€{num:,.2f}"
    if currency == "KES":
        return f"KSh {num:,.2f}"
    if currency == "GHS":
        return f"GH₵{num:,.2f}"
    return f"{currency} {num:,.2f}"


# ── Welcome Email ────────────────────────────────────────────────────────

def send_welcome_email(email: str, full_name: str, business_name: str = "") -> Dict[str, Any]:
    """Send welcome email after successful registration."""
    name = full_name or email.split("@")[0]
    biz = business_name or "your business"

    html = _wrap_html(f"""
    {_header("Welcome to SME Control Tower", "Your AI-powered business assistant")}
    <div class="body">
      <h2>Welcome, {name}! 🎉</h2>
      <p>Your account for <strong>{biz}</strong> is ready. You're now set up with our
      <strong>Starter plan (free)</strong> — no credit card needed.</p>
      <p>Here's what you can do right away:</p>
      <ul style="font-size:14px; padding-left:20px;">
        <li>Upload invoices, receipts, or bank statements</li>
        <li>Create and send professional invoices to customers</li>
        <li>Get AI-powered insights on your cash flow</li>
        <li>Track inventory and supplier relationships</li>
        <li>Monitor business health with your BSI score</li>
      </ul>
      <p style="margin-top:20px;">
        <a href="{settings.cors_origins.split(',')[0].strip()}/dashboard" class="btn">Go to Dashboard</a>
      </p>
      <p style="margin-top:20px; font-size:13px; color:#64748b;">
        Need help? Visit the Help section in your dashboard or reply to this email.
      </p>
    </div>
    {_footer()}
    """)

    text = f"Welcome to SME Control Tower, {name}! Your account for {biz} is ready. Log in to get started."

    try:
        ses = get_ses_service()
        return ses.send_email(to=email, subject=f"Welcome to SME Control Tower, {name}!", body_text=text, body_html=html)
    except Exception as exc:
        logger.warning("Failed to send welcome email to %s: %s", email, exc)
        return {"status": "failed", "error": str(exc)}


# ── Invoice Delivery Email ───────────────────────────────────────────────

def send_invoice_email(invoice: Dict[str, Any], public_url: str = "") -> Dict[str, Any]:
    """Send invoice to customer when status changes to 'sent'."""
    customer_email = invoice.get("customer_email", "")
    if not customer_email:
        logger.info("No customer email on invoice %s — skipping delivery", invoice.get("invoice_id"))
        return {"status": "skipped", "reason": "no_customer_email"}

    currency = invoice.get("currency", "NGN")
    total = _fmt_currency(invoice.get("total", 0), currency)
    biz_name = invoice.get("business_name", "SME Control Tower")
    inv_number = invoice.get("invoice_number", "")
    customer_name = invoice.get("customer_name", "Customer")
    due_date = invoice.get("due_date", "")

    # Build line items table
    items_html = ""
    for item in invoice.get("line_items", []):
        amt = item.get("amount", item.get("quantity", 0) * item.get("unit_price", 0))
        items_html += f"""<tr>
          <td>{item.get('description', '')}</td>
          <td style="text-align:right">{item.get('quantity', 0)}</td>
          <td style="text-align:right">{_fmt_currency(item.get('unit_price', 0), currency)}</td>
          <td style="text-align:right">{_fmt_currency(amt, currency)}</td>
        </tr>"""

    pay_btn = ""
    if public_url:
        pay_btn = f'<p style="margin-top:20px;text-align:center;"><a href="{public_url}" class="btn btn-green">View Invoice & Pay</a></p>'

    html = _wrap_html(f"""
    {_header(f"Invoice {inv_number}", f"From {biz_name}")}
    <div class="body">
      <p>Dear {customer_name},</p>
      <p>Please find your invoice below. The total amount due is <strong>{total}</strong>,
      payable by <strong>{due_date}</strong>.</p>
      <table class="table">
        <thead><tr><th>Description</th><th style="text-align:right">Qty</th>
        <th style="text-align:right">Unit Price</th><th style="text-align:right">Amount</th></tr></thead>
        <tbody>{items_html}</tbody>
      </table>
      <div style="text-align:right;margin-top:8px;">
        <p style="font-size:13px;color:#64748b;">Subtotal: {_fmt_currency(invoice.get('subtotal', 0), currency)}</p>
        <p style="font-size:16px;font-weight:700;">Total: {total}</p>
      </div>
      {pay_btn}
      <p style="margin-top:20px;font-size:13px;color:#64748b;">
        If you have questions about this invoice, please contact {biz_name} directly.
      </p>
    </div>
    {_footer()}
    """)

    text = f"Invoice {inv_number} from {biz_name}. Amount due: {total} by {due_date}."
    if public_url:
        text += f" View and pay: {public_url}"

    try:
        ses = get_ses_service()
        return ses.send_email(
            to=customer_email,
            subject=f"Invoice {inv_number} from {biz_name} — {total} due {due_date}",
            body_text=text,
            body_html=html,
        )
    except Exception as exc:
        logger.warning("Failed to send invoice email for %s: %s", inv_number, exc)
        return {"status": "failed", "error": str(exc)}


# ── Payment Confirmation Email ───────────────────────────────────────────

def send_payment_confirmation(invoice: Dict[str, Any], to_customer: bool = True, to_business: bool = True) -> Dict[str, Any]:
    """Send payment confirmation when invoice is marked as paid."""
    currency = invoice.get("currency", "NGN")
    total = _fmt_currency(invoice.get("total", 0), currency)
    biz_name = invoice.get("business_name", "SME Control Tower")
    inv_number = invoice.get("invoice_number", "")
    customer_name = invoice.get("customer_name", "Customer")
    paid_date = invoice.get("paid_date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    results = {}

    # Email to customer
    customer_email = invoice.get("customer_email", "")
    if to_customer and customer_email:
        html = _wrap_html(f"""
        {_header("Payment Confirmed ✓", f"Invoice {inv_number}")}
        <div class="body">
          <p>Dear {customer_name},</p>
          <p>We've received your payment of <strong>{total}</strong> for invoice
          <strong>{inv_number}</strong>. Thank you!</p>
          <div style="background:#f0fdf4;border-radius:8px;padding:16px;margin:16px 0;text-align:center;">
            <span class="badge badge-paid">PAID</span>
            <p style="margin:8px 0 0;font-size:18px;font-weight:700;color:#166534;">{total}</p>
            <p style="margin:4px 0 0;font-size:12px;color:#64748b;">Paid on {paid_date}</p>
          </div>
          <p style="font-size:13px;color:#64748b;">This email serves as your payment receipt.
          Keep it for your records.</p>
        </div>
        {_footer()}
        """)
        try:
            ses = get_ses_service()
            results["customer"] = ses.send_email(
                to=customer_email,
                subject=f"Payment received — Invoice {inv_number} ({total})",
                body_text=f"Payment of {total} received for invoice {inv_number}. Thank you!",
                body_html=html,
            )
        except Exception as exc:
            logger.warning("Failed to send payment confirmation to customer: %s", exc)
            results["customer"] = {"status": "failed", "error": str(exc)}

    # Email to business owner
    biz_email = invoice.get("business_email", "")
    if to_business and biz_email:
        html = _wrap_html(f"""
        {_header("Payment Received 💰", f"Invoice {inv_number}")}
        <div class="body">
          <p>Good news! <strong>{customer_name}</strong> has paid invoice
          <strong>{inv_number}</strong>.</p>
          <div style="background:#f0fdf4;border-radius:8px;padding:16px;margin:16px 0;text-align:center;">
            <p style="margin:0;font-size:22px;font-weight:700;color:#166534;">{total}</p>
            <p style="margin:4px 0 0;font-size:12px;color:#64748b;">Received on {paid_date}</p>
          </div>
          <p style="font-size:13px;color:#64748b;">Log in to your dashboard to see updated invoice stats.</p>
        </div>
        {_footer()}
        """)
        try:
            ses = get_ses_service()
            results["business"] = ses.send_email(
                to=biz_email,
                subject=f"💰 Payment received from {customer_name} — {total}",
                body_text=f"{customer_name} paid {total} for invoice {inv_number}.",
                body_html=html,
            )
        except Exception as exc:
            logger.warning("Failed to send payment notification to business: %s", exc)
            results["business"] = {"status": "failed", "error": str(exc)}

    return results


# ── Overdue Reminder Email ───────────────────────────────────────────────

def send_overdue_reminder(invoice: Dict[str, Any], public_url: str = "") -> Dict[str, Any]:
    """Send overdue payment reminder to customer."""
    customer_email = invoice.get("customer_email", "")
    if not customer_email:
        return {"status": "skipped", "reason": "no_customer_email"}

    currency = invoice.get("currency", "NGN")
    total = _fmt_currency(invoice.get("total", 0), currency)
    biz_name = invoice.get("business_name", "SME Control Tower")
    inv_number = invoice.get("invoice_number", "")
    customer_name = invoice.get("customer_name", "Customer")
    due_date = invoice.get("due_date", "")

    pay_btn = ""
    if public_url:
        pay_btn = f'<p style="margin-top:20px;text-align:center;"><a href="{public_url}" class="btn">Pay Now</a></p>'

    html = _wrap_html(f"""
    {_header("Payment Reminder", f"Invoice {inv_number} — Overdue")}
    <div class="body">
      <p>Dear {customer_name},</p>
      <p>This is a friendly reminder that invoice <strong>{inv_number}</strong> for
      <strong>{total}</strong> was due on <strong>{due_date}</strong> and is now overdue.</p>
      <div style="background:#fef2f2;border-radius:8px;padding:16px;margin:16px 0;text-align:center;">
        <span class="badge badge-overdue">OVERDUE</span>
        <p style="margin:8px 0 0;font-size:18px;font-weight:700;color:#991b1b;">{total}</p>
        <p style="margin:4px 0 0;font-size:12px;color:#64748b;">Due date: {due_date}</p>
      </div>
      {pay_btn}
      <p style="font-size:13px;color:#64748b;">
        If you've already made this payment, please disregard this reminder.
        For questions, contact {biz_name} directly.
      </p>
    </div>
    {_footer()}
    """)

    text = f"Reminder: Invoice {inv_number} for {total} from {biz_name} was due {due_date} and is overdue."

    try:
        ses = get_ses_service()
        return ses.send_email(
            to=customer_email,
            subject=f"⚠️ Overdue: Invoice {inv_number} — {total} from {biz_name}",
            body_text=text,
            body_html=html,
        )
    except Exception as exc:
        logger.warning("Failed to send overdue reminder for %s: %s", inv_number, exc)
        return {"status": "failed", "error": str(exc)}


# ── Generic Notification ─────────────────────────────────────────────────

def send_notification(email: str, subject: str, message: str, cta_text: str = "", cta_url: str = "") -> Dict[str, Any]:
    """Send a generic platform notification email."""
    cta = ""
    if cta_text and cta_url:
        cta = f'<p style="margin-top:20px;"><a href="{cta_url}" class="btn">{cta_text}</a></p>'

    html = _wrap_html(f"""
    {_header("SME Control Tower")}
    <div class="body">
      <p>{message}</p>
      {cta}
    </div>
    {_footer()}
    """)

    try:
        ses = get_ses_service()
        return ses.send_email(to=email, subject=subject, body_text=message, body_html=html)
    except Exception as exc:
        logger.warning("Failed to send notification to %s: %s", email, exc)
        return {"status": "failed", "error": str(exc)}
