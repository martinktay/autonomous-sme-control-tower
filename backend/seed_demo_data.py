"""Seed realistic Nigerian SME demo data into DynamoDB for hackathon demo."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.ddb_service import get_ddb_service
from app.utils.id_generator import generate_id
from datetime import datetime, timedelta, timezone

ddb = get_ddb_service()
ORG = "demo-org-001"
now = datetime.now(timezone.utc)


def ts(days_ago=0, hours_ago=0):
    return (now - timedelta(days=days_ago, hours=hours_ago)).isoformat()


# ── Signals (invoices + emails) ──────────────────────────────────
signals = [
    {
        "org_id": ORG, "signal_id": generate_id("signal"),
        "signal_type": "invoice", "processing_status": "processed",
        "content": {
            "vendor_name": "Lagos Paper Supplies Ltd",
            "invoice_id": "INV-2026-0041",
            "amount": 450000.00, "currency": "NGN",
            "due_date": ts(-5), "description": "Office supplies Q1 2026"
        },
        "created_at": ts(12)
    },
    {
        "org_id": ORG, "signal_id": generate_id("signal"),
        "signal_type": "invoice", "processing_status": "processed",
        "content": {
            "vendor_name": "Dangote Cement PLC",
            "invoice_id": "INV-2026-0042",
            "amount": 2800000.00, "currency": "NGN",
            "due_date": ts(5), "description": "Building materials for warehouse expansion"
        },
        "created_at": ts(10)
    },
    {
        "org_id": ORG, "signal_id": generate_id("signal"),
        "signal_type": "invoice", "processing_status": "processed",
        "content": {
            "vendor_name": "MTN Business Nigeria",
            "invoice_id": "INV-2026-0043",
            "amount": 185000.00, "currency": "NGN",
            "due_date": ts(-2), "description": "Internet and telecom services Feb 2026"
        },
        "created_at": ts(8)
    },
    {
        "org_id": ORG, "signal_id": generate_id("signal"),
        "signal_type": "invoice", "processing_status": "processed",
        "content": {
            "vendor_name": "Ibadan Logistics Co",
            "invoice_id": "INV-2026-0044",
            "amount": 920000.00, "currency": "NGN",
            "due_date": ts(15), "description": "Freight and delivery services"
        },
        "created_at": ts(6)
    },
    {
        "org_id": ORG, "signal_id": generate_id("signal"),
        "signal_type": "email", "processing_status": "processed",
        "content": {
            "sender": "accounts@lagospaper.ng",
            "subject": "Payment Reminder: INV-2026-0041 Overdue",
            "classification": "payment_reminder",
            "body": "Dear Customer, your invoice INV-2026-0041 for NGN 450,000 is now 5 days overdue."
        },
        "created_at": ts(4)
    },
    {
        "org_id": ORG, "signal_id": generate_id("signal"),
        "signal_type": "email", "processing_status": "processed",
        "content": {
            "sender": "procurement@clientcorp.ng",
            "subject": "New Purchase Order #PO-8821",
            "classification": "customer_inquiry",
            "body": "We would like to place an order for 500 units. Please confirm availability."
        },
        "created_at": ts(3)
    },
    {
        "org_id": ORG, "signal_id": generate_id("signal"),
        "signal_type": "email", "processing_status": "processed",
        "content": {
            "sender": "ops@ibadanlogistics.ng",
            "subject": "Delivery Delay Notice - Shipment #SH-4412",
            "classification": "operational_message",
            "body": "Due to road conditions, shipment SH-4412 will be delayed by 3 days."
        },
        "created_at": ts(2)
    },
]

for s in signals:
    ddb.create_signal(s)
print(f"Created {len(signals)} signals")


# ══════════════════════════════════════════════════════════════════
# ORG 2: GreenField Farms — Agriculture
# ══════════════════════════════════════════════════════════════════
ORG2 = "demo-org-002"

signals_org2 = [
    {
        "org_id": ORG2, "signal_id": generate_id("signal"),
        "signal_type": "invoice", "processing_status": "processed",
        "content": {
            "vendor_name": "Ajaokuta Fertilizer Co",
            "invoice_id": "INV-2026-1001",
            "amount": 1200000.00, "currency": "NGN",
            "due_date": ts(10), "description": "NPK fertilizer for planting season"
        },
        "created_at": ts(14)
    },
    {
        "org_id": ORG2, "signal_id": generate_id("signal"),
        "signal_type": "invoice", "processing_status": "processed",
        "content": {
            "vendor_name": "Ogun Tractor Rentals",
            "invoice_id": "INV-2026-1002",
            "amount": 750000.00, "currency": "NGN",
            "due_date": ts(-3), "description": "Tractor hire for land preparation"
        },
        "created_at": ts(11)
    },
    {
        "org_id": ORG2, "signal_id": generate_id("signal"),
        "signal_type": "invoice", "processing_status": "processed",
        "content": {
            "vendor_name": "SeedCo Nigeria Ltd",
            "invoice_id": "INV-2026-1003",
            "amount": 480000.00, "currency": "NGN",
            "due_date": ts(20), "description": "Hybrid maize seeds — 200 bags"
        },
        "created_at": ts(9)
    },
    {
        "org_id": ORG2, "signal_id": generate_id("signal"),
        "signal_type": "invoice", "processing_status": "processed",
        "content": {
            "vendor_name": "Kano Irrigation Supplies",
            "invoice_id": "INV-2026-1004",
            "amount": 2100000.00, "currency": "NGN",
            "due_date": ts(7), "description": "Drip irrigation system installation"
        },
        "created_at": ts(7)
    },
    {
        "org_id": ORG2, "signal_id": generate_id("signal"),
        "signal_type": "email", "processing_status": "processed",
        "content": {
            "sender": "finance@oguntractors.ng",
            "subject": "Overdue Payment: INV-2026-1002",
            "classification": "payment_reminder",
            "body": "Dear GreenField Farms, your invoice INV-2026-1002 for NGN 750,000 is 3 days overdue. Please remit payment."
        },
        "created_at": ts(3)
    },
    {
        "org_id": ORG2, "signal_id": generate_id("signal"),
        "signal_type": "email", "processing_status": "processed",
        "content": {
            "sender": "buyer@josmarket.ng",
            "subject": "Bulk Maize Purchase Inquiry — 50 Tonnes",
            "classification": "customer_inquiry",
            "body": "Good day, we are interested in purchasing 50 tonnes of maize for Q2 delivery. Kindly share pricing."
        },
        "created_at": ts(2)
    },
    {
        "org_id": ORG2, "signal_id": generate_id("signal"),
        "signal_type": "email", "processing_status": "processed",
        "content": {
            "sender": "weather@farmadvisory.ng",
            "subject": "Rainfall Alert: Below Average Expected in March",
            "classification": "operational_message",
            "body": "Advisory: March rainfall in your region is projected 30% below average. Consider activating irrigation early."
        },
        "created_at": ts(1)
    },
]

for s in signals_org2:
    ddb.create_signal(s)
print(f"Created {len(signals_org2)} signals for GreenField Farms")


# ══════════════════════════════════════════════════════════════════
# ORG 3: TechBridge Solutions — IT Services
# ══════════════════════════════════════════════════════════════════
ORG3 = "demo-org-003"

signals_org3 = [
    {
        "org_id": ORG3, "signal_id": generate_id("signal"),
        "signal_type": "invoice", "processing_status": "processed",
        "content": {
            "vendor_name": "AWS Nigeria (via Flutterwave)",
            "invoice_id": "INV-2026-2001",
            "amount": 890000.00, "currency": "NGN",
            "due_date": ts(5), "description": "Cloud hosting and compute — Feb 2026"
        },
        "created_at": ts(12)
    },
    {
        "org_id": ORG3, "signal_id": generate_id("signal"),
        "signal_type": "invoice", "processing_status": "processed",
        "content": {
            "vendor_name": "Andela Talent Services",
            "invoice_id": "INV-2026-2002",
            "amount": 3500000.00, "currency": "NGN",
            "due_date": ts(-7), "description": "Contract developer staffing — 2 senior engineers"
        },
        "created_at": ts(10)
    },
    {
        "org_id": ORG3, "signal_id": generate_id("signal"),
        "signal_type": "invoice", "processing_status": "processed",
        "content": {
            "vendor_name": "MainOne Data Centre",
            "invoice_id": "INV-2026-2003",
            "amount": 420000.00, "currency": "NGN",
            "due_date": ts(15), "description": "Colocation and bandwidth — Q1 2026"
        },
        "created_at": ts(8)
    },
    {
        "org_id": ORG3, "signal_id": generate_id("signal"),
        "signal_type": "invoice", "processing_status": "processed",
        "content": {
            "vendor_name": "Interswitch Payment Gateway",
            "invoice_id": "INV-2026-2004",
            "amount": 165000.00, "currency": "NGN",
            "due_date": ts(3), "description": "Payment processing fees — February"
        },
        "created_at": ts(5)
    },
    {
        "org_id": ORG3, "signal_id": generate_id("signal"),
        "signal_type": "email", "processing_status": "processed",
        "content": {
            "sender": "billing@andela.com",
            "subject": "Urgent: Invoice INV-2026-2002 Past Due",
            "classification": "payment_reminder",
            "body": "Hi TechBridge, invoice INV-2026-2002 for NGN 3,500,000 is now 7 days overdue. Please arrange payment to avoid service interruption."
        },
        "created_at": ts(4)
    },
    {
        "org_id": ORG3, "signal_id": generate_id("signal"),
        "signal_type": "email", "processing_status": "processed",
        "content": {
            "sender": "cto@fintechstartup.ng",
            "subject": "RFP: Mobile Banking App Development",
            "classification": "customer_inquiry",
            "body": "We are looking for a development partner to build our mobile banking platform. Budget is NGN 25M. Can we schedule a call?"
        },
        "created_at": ts(2)
    },
    {
        "org_id": ORG3, "signal_id": generate_id("signal"),
        "signal_type": "email", "processing_status": "processed",
        "content": {
            "sender": "hr@techbridge.ng",
            "subject": "Staff Attrition Alert: 2 Resignations This Month",
            "classification": "operational_message",
            "body": "Two mid-level developers have submitted resignation letters. Current team capacity is at 70%. Recommend urgent hiring."
        },
        "created_at": ts(1)
    },
]

for s in signals_org3:
    ddb.create_signal(s)
print(f"Created {len(signals_org3)} signals for TechBridge Solutions")


# ══════════════════════════════════════════════════════════════════
# ORG 4: Brighton Craft Bakery — UK Food & Beverage
# ══════════════════════════════════════════════════════════════════
ORG4 = "demo-org-004"

signals_org4 = [
    {
        "org_id": ORG4, "signal_id": generate_id("signal"),
        "signal_type": "invoice", "processing_status": "processed",
        "content": {
            "vendor_name": "Wessex Flour Mills",
            "invoice_id": "INV-2026-4001",
            "amount": 2800.00, "currency": "GBP",
            "due_date": ts(-4), "description": "Organic bread flour — 2 tonnes"
        },
        "created_at": ts(14)
    },
    {
        "org_id": ORG4, "signal_id": generate_id("signal"),
        "signal_type": "invoice", "processing_status": "processed",
        "content": {
            "vendor_name": "South Downs Dairy",
            "invoice_id": "INV-2026-4002",
            "amount": 1450.00, "currency": "GBP",
            "due_date": ts(7), "description": "Butter, cream, and eggs — weekly supply"
        },
        "created_at": ts(10)
    },
    {
        "org_id": ORG4, "signal_id": generate_id("signal"),
        "signal_type": "invoice", "processing_status": "processed",
        "content": {
            "vendor_name": "British Gas Business",
            "invoice_id": "INV-2026-4003",
            "amount": 890.00, "currency": "GBP",
            "due_date": ts(-10), "description": "Gas supply — bakery ovens Feb 2026"
        },
        "created_at": ts(9)
    },
    {
        "org_id": ORG4, "signal_id": generate_id("signal"),
        "signal_type": "invoice", "processing_status": "processed",
        "content": {
            "vendor_name": "PackRight UK Ltd",
            "invoice_id": "INV-2026-4004",
            "amount": 620.00, "currency": "GBP",
            "due_date": ts(12), "description": "Branded packaging and cake boxes"
        },
        "created_at": ts(7)
    },
    {
        "org_id": ORG4, "signal_id": generate_id("signal"),
        "signal_type": "email", "processing_status": "processed",
        "content": {
            "sender": "accounts@wessexflour.co.uk",
            "subject": "Payment Overdue: INV-2026-4001",
            "classification": "payment_reminder",
            "body": "Dear Brighton Craft Bakery, your invoice INV-2026-4001 for GBP 2,800 is now 4 days overdue. Please arrange payment."
        },
        "created_at": ts(3)
    },
    {
        "org_id": ORG4, "signal_id": generate_id("signal"),
        "signal_type": "email", "processing_status": "processed",
        "content": {
            "sender": "events@brightoncouncil.gov.uk",
            "subject": "Catering Opportunity: Brighton Food Festival 2026",
            "classification": "customer_inquiry",
            "body": "We are inviting local bakeries to supply pastries for the Brighton Food Festival in April. Estimated order: 2,000 units over 3 days."
        },
        "created_at": ts(2)
    },
    {
        "org_id": ORG4, "signal_id": generate_id("signal"),
        "signal_type": "email", "processing_status": "processed",
        "content": {
            "sender": "manager@brightoncraftbakery.co.uk",
            "subject": "Oven Maintenance Due — Unit 2 Showing Faults",
            "classification": "operational_message",
            "body": "The main deck oven (Unit 2) is showing temperature inconsistencies. Engineer visit recommended before it fails completely."
        },
        "created_at": ts(1)
    },
]

for s in signals_org4:
    ddb.create_signal(s)
print(f"Created {len(signals_org4)} signals for Brighton Craft Bakery")


# ══════════════════════════════════════════════════════════════════
# ORG 5: Thames Valley Plumbing — UK Trade Services
# ══════════════════════════════════════════════════════════════════
ORG5 = "demo-org-005"

signals_org5 = [
    {
        "org_id": ORG5, "signal_id": generate_id("signal"),
        "signal_type": "invoice", "processing_status": "processed",
        "content": {
            "vendor_name": "Screwfix Trade Account",
            "invoice_id": "INV-2026-5001",
            "amount": 1340.00, "currency": "GBP",
            "due_date": ts(10), "description": "Copper pipe, fittings, and sealant — monthly stock"
        },
        "created_at": ts(12)
    },
    {
        "org_id": ORG5, "signal_id": generate_id("signal"),
        "signal_type": "invoice", "processing_status": "processed",
        "content": {
            "vendor_name": "Vaillant Boilers UK",
            "invoice_id": "INV-2026-5002",
            "amount": 4200.00, "currency": "GBP",
            "due_date": ts(-6), "description": "3x combi boiler units for customer installs"
        },
        "created_at": ts(10)
    },
    {
        "org_id": ORG5, "signal_id": generate_id("signal"),
        "signal_type": "invoice", "processing_status": "processed",
        "content": {
            "vendor_name": "Ford Transit Leasing",
            "invoice_id": "INV-2026-5003",
            "amount": 580.00, "currency": "GBP",
            "due_date": ts(3), "description": "Monthly van lease — 2 Transit Custom vans"
        },
        "created_at": ts(8)
    },
    {
        "org_id": ORG5, "signal_id": generate_id("signal"),
        "signal_type": "invoice", "processing_status": "processed",
        "content": {
            "vendor_name": "Simply Business Insurance",
            "invoice_id": "INV-2026-5004",
            "amount": 320.00, "currency": "GBP",
            "due_date": ts(20), "description": "Public liability insurance — quarterly premium"
        },
        "created_at": ts(5)
    },
    {
        "org_id": ORG5, "signal_id": generate_id("signal"),
        "signal_type": "email", "processing_status": "processed",
        "content": {
            "sender": "trade@vaillant.co.uk",
            "subject": "Overdue: INV-2026-5002 — Please Remit",
            "classification": "payment_reminder",
            "body": "Dear Thames Valley Plumbing, invoice INV-2026-5002 for GBP 4,200 is 6 days past due. Continued late payment may affect your trade discount."
        },
        "created_at": ts(4)
    },
    {
        "org_id": ORG5, "signal_id": generate_id("signal"),
        "signal_type": "email", "processing_status": "processed",
        "content": {
            "sender": "lettings@oxfordproperty.co.uk",
            "subject": "Ongoing Contract: 12 Properties — Plumbing Maintenance",
            "classification": "customer_inquiry",
            "body": "We manage 12 rental properties in Oxford and need a reliable plumber on retainer. Would you be interested in a 12-month contract?"
        },
        "created_at": ts(2)
    },
    {
        "org_id": ORG5, "signal_id": generate_id("signal"),
        "signal_type": "email", "processing_status": "processed",
        "content": {
            "sender": "admin@thamesvalleyplumbing.co.uk",
            "subject": "Apprentice Certification Expiring — Action Needed",
            "classification": "operational_message",
            "body": "Jake's Gas Safe certification expires in 3 weeks. He needs to complete the renewal course or he cannot work on boiler installs."
        },
        "created_at": ts(1)
    },
]

for s in signals_org5:
    ddb.create_signal(s)
print(f"Created {len(signals_org5)} signals for Thames Valley Plumbing")

print("\nDone! Seed data created for all 5 demo organisations.")
