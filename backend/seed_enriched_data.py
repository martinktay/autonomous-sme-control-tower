"""
Seed enriched, realistic data for ALL businesses to light up every dashboard.

Populates: transactions, inventory, counterparties, alerts, signals, NSI scores,
strategies, actions, evaluations, insights, and businesses table.

Covers all 9 test accounts (3 Nigerian + 5 multi-country + 1 super admin).

Usage:
  cd backend
  python seed_enriched_data.py
"""

import sys
import os
import random
from datetime import datetime, timezone, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(__file__))

import boto3
from app.config import get_settings
from app.utils.id_generator import generate_id

settings = get_settings()

ddb = boto3.resource(
    "dynamodb",
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_access_key_id or None,
    aws_secret_access_key=settings.aws_secret_access_key or None,
)

# All tables
txn_table = ddb.Table(settings.transactions_table)
inv_table = ddb.Table(settings.inventory_table)
cp_table = ddb.Table(settings.counterparties_table)
alert_table = ddb.Table(settings.alerts_table)
signals_table = ddb.Table(settings.signals_table)
nsi_table = ddb.Table(settings.nsi_scores_table)
strategies_table = ddb.Table(settings.strategies_table)
actions_table = ddb.Table(settings.actions_table)
evaluations_table = ddb.Table(settings.evaluations_table)
insights_table = ddb.Table(settings.insights_table)
businesses_table = ddb.Table(settings.businesses_table)
users_table = ddb.Table(settings.users_table)

now = datetime.now(timezone.utc)


def _id(entity: str) -> str:
    return generate_id(entity)


def dec(v):
    return Decimal(str(round(v, 2)))


def iso(dt):
    return dt.isoformat()


def get_org_id(email):
    resp = users_table.get_item(Key={"email": email})
    item = resp.get("Item")
    if not item:
        print(f"  WARNING: User {email} not found — skipping")
        return None
    return item["org_id"]


# ═══════════════════════════════════════════════════════════════
# BUSINESS PROFILES — data config per account
# ═══════════════════════════════════════════════════════════════

BUSINESSES = {
    "starter@demo.com": {
        "name": "Ade's Trading Co",
        "type": "supermarket",
        "country": "NG",
        "currency": "NGN",
        "tier": "starter",
        "suppliers": [
            ("Dangote Industries", "+2348012345678"),
            ("Nigerian Breweries", "+2348023456789"),
            ("Unilever Nigeria", "+2348034567890"),
            ("PZ Cussons", "+2348045678901"),
            ("Nestle Nigeria", "+2348056789012"),
        ],
        "customers": [
            ("Mama Nkechi Shop", "+2348067890123"),
            ("Ikeja Mini Mart", "+2348078901234"),
            ("Surulere Provisions", "+2348089012345"),
        ],
        "products": [
            ("Golden Penny Semovita 10kg", "Grains", 45, 4200, 5500, 20),
            ("Peak Milk Tin 400g", "Dairy", 120, 850, 1100, 30),
            ("Indomie Carton (40 packs)", "Noodles", 35, 5800, 7200, 15),
            ("Coca-Cola Crate (24 bottles)", "Beverages", 28, 4500, 5800, 10),
            ("Dangote Sugar 50kg", "Sugar", 18, 38000, 42000, 8),
            ("Kings Oil 5L", "Cooking Oil", 40, 6500, 8200, 12),
            ("Dettol Soap (Carton)", "Toiletries", 22, 3200, 4500, 10),
            ("Milo 400g Tin", "Beverages", 65, 1800, 2400, 25),
            ("Maggi Cubes (Carton)", "Seasoning", 50, 2800, 3600, 20),
            ("Bournvita 400g", "Beverages", 38, 1600, 2200, 15),
        ],
        "rev_categories": ["Provisions Sales", "Beverages Sales", "Wholesale Order", "Walk-in Customer"],
        "exp_categories": ["Stock Purchase", "Rent", "Transport/Logistics", "Staff Salary", "Electricity", "Phone/Data"],
        "rev_range": (5000, 85000),
        "exp_range": (3000, 50000),
        "daily_rev_count": (3, 6),
        "daily_exp_count": (1, 2),
        "nsi_base": 62,
        "alerts": [
            ("low_stock", "warning", "Low Stock: Dangote Sugar 50kg", "Only 18 bags remaining. Reorder point is 8 but sales velocity suggests stockout in 5 days.", "Place order with Dangote Industries for 30 bags"),
            ("cashflow_warning", "critical", "Cash Flow Pressure This Week", "Outgoing payments of ₦485,000 due but projected revenue is ₦320,000.", "Delay non-urgent stock purchases or collect outstanding receivables"),
            ("overdue_payment", "warning", "Overdue: Ikeja Mini Mart owes ₦67,500", "Invoice from 14 days ago still unpaid. Customer usually pays within 7 days.", "Send payment reminder via WhatsApp"),
            ("expense_spike", "info", "Transport costs up 15% this month", "Logistics spending increased from ₦42,000 to ₦48,300 weekly average.", "Negotiate bulk delivery rates with transporter"),
        ],
        "signals": [
            ("invoice", {"vendor_name": "Dangote Industries", "invoice_id": "INV-2026-0101", "amount": 684000.00, "currency": "NGN", "due_date": 5, "description": "Sugar and cement supplies — March batch"}),
            ("invoice", {"vendor_name": "Nigerian Breweries", "invoice_id": "INV-2026-0102", "amount": 312000.00, "currency": "NGN", "due_date": -3, "description": "Beverages restock — Coca-Cola, Malt, Star"}),
            ("invoice", {"vendor_name": "PZ Cussons", "invoice_id": "INV-2026-0103", "amount": 156000.00, "currency": "NGN", "due_date": 10, "description": "Toiletries and soap cartons"}),
            ("email", {"sender": "accounts@dangote.com.ng", "subject": "Payment Reminder: INV-2026-0101", "classification": "payment_reminder", "body": "Dear Ade's Trading, your invoice INV-2026-0101 for NGN 684,000 is due in 5 days."}),
            ("email", {"sender": "procurement@ikejaminimart.ng", "subject": "Bulk Order Request — 50 Cartons Indomie", "classification": "customer_inquiry", "body": "We need 50 cartons of Indomie for next week delivery. Please confirm stock and pricing."}),
            ("email", {"sender": "ops@adestrading.ng", "subject": "Generator Fuel Cost Rising", "classification": "operational_message", "body": "Diesel price increased to ₦1,200/litre. Monthly generator cost now ₦85,000 vs ₦62,000 last month."}),
        ],
    },
    "growth@demo.com": {
        "name": "GreenField Farms",
        "type": "agriculture",
        "country": "NG",
        "currency": "NGN",
        "tier": "growth",
        "suppliers": [
            ("Agro-Allied Chemicals", "+2348112345678"),
            ("Tractor Hire Services", "+2348123456789"),
            ("Seed Nigeria Ltd", "+2348134567890"),
        ],
        "customers": [
            ("Lagos Garri Factory", "+2348145678901"),
            ("Sango Market Traders", "+2348156789012"),
            ("FoodCo Supermarket", "+2348167890123"),
            ("Shoprite Nigeria", "+2348178901234"),
        ],
        "products": [
            ("Cassava (Tonnes)", "Root Crops", 12, 85000, 120000, 5),
            ("Maize (Bags 100kg)", "Grains", 45, 28000, 38000, 15),
            ("Tomatoes (Baskets)", "Vegetables", 30, 8000, 15000, 10),
            ("Pepper (Bags)", "Vegetables", 25, 12000, 22000, 8),
            ("Palm Oil (25L Jerrycans)", "Oil", 20, 18000, 28000, 8),
            ("Fertilizer NPK (Bags)", "Inputs", 35, 15000, 0, 10),
            ("Herbicide (Litres)", "Inputs", 50, 3500, 0, 15),
        ],
        "rev_categories": ["Cassava Sales", "Maize Sales", "Vegetable Sales", "Palm Oil Sales"],
        "exp_categories": ["Farm Labour", "Fertilizer", "Transport", "Equipment Hire", "Diesel/Fuel", "Seeds"],
        "rev_range": (25000, 250000),
        "exp_range": (10000, 120000),
        "daily_rev_count": (1, 3),
        "daily_exp_count": (0, 2),
        "nsi_base": 55,
        "alerts": [
            ("low_stock", "warning", "Fertilizer Running Low", "Only 35 bags of NPK remaining. Next planting season starts in 3 weeks.", "Order 50 bags from Agro-Allied Chemicals"),
            ("overdue_payment", "critical", "FoodCo Supermarket: ₦180,000 Overdue", "Delivery made 21 days ago, payment terms were 14 days.", "Call procurement manager and send formal reminder"),
            ("expense_spike", "info", "Transport Costs Up 40%", "Fuel price increase has pushed logistics costs from ₦45,000 to ₦63,000 per week.", "Consider bulk transport scheduling to reduce trips"),
            ("seasonal_risk", "warning", "Dry Season Approaching", "Rainfall dropping below average. Irrigation may be needed for tomato and pepper crops.", "Activate drip irrigation system and budget for water costs"),
        ],
        "signals": [
            ("invoice", {"vendor_name": "Agro-Allied Chemicals", "invoice_id": "INV-2026-1001", "amount": 525000.00, "currency": "NGN", "due_date": 10, "description": "NPK fertilizer — 35 bags for planting season"}),
            ("invoice", {"vendor_name": "Tractor Hire Services", "invoice_id": "INV-2026-1002", "amount": 750000.00, "currency": "NGN", "due_date": -3, "description": "Tractor hire for land preparation — 15 hectares"}),
            ("invoice", {"vendor_name": "Seed Nigeria Ltd", "invoice_id": "INV-2026-1003", "amount": 280000.00, "currency": "NGN", "due_date": 20, "description": "Hybrid maize seeds — 100 bags"}),
            ("email", {"sender": "buyer@foodco.ng", "subject": "Bulk Cassava Purchase — 20 Tonnes", "classification": "customer_inquiry", "body": "We need 20 tonnes of cassava for our processing plant. Delivery within 2 weeks. Please quote."}),
            ("email", {"sender": "weather@farmadvisory.ng", "subject": "Rainfall Alert: Below Average Expected", "classification": "operational_message", "body": "March rainfall projected 30% below average in your region. Activate irrigation early."}),
            ("email", {"sender": "finance@oguntractors.ng", "subject": "Overdue Payment: INV-2026-1002", "classification": "payment_reminder", "body": "Your invoice for NGN 750,000 is 3 days overdue. Please remit payment."}),
        ],
    },
    "business@demo.com": {
        "name": "TechBridge Solutions",
        "type": "professional_service",
        "country": "NG",
        "currency": "NGN",
        "tier": "business",
        "suppliers": [
            ("AWS Nigeria", "+2348212345678"),
            ("Konga Office Supplies", "+2348223456789"),
            ("MainOne Internet", "+2348234567890"),
            ("Andela Talent Services", "+2348241234567"),
            ("Google Workspace Reseller", "+2348252345678"),
        ],
        "customers": [
            ("First Bank Nigeria", "+2348245678901"),
            ("GTBank", "+2348256789012"),
            ("Flutterwave", "+2348267890123"),
            ("Paystack", "+2348278901234"),
            ("Interswitch", "+2348289012345"),
            ("Sterling Bank", "+2348290123456"),
            ("Dangote Group IT", "+2348201234567"),
            ("Access Bank", "+2348202345678"),
        ],
        "products": [
            ("AWS Credits (Monthly)", "Cloud Services", 1, 450000, 650000, 1),
            ("Microsoft 365 Licenses", "Software", 25, 8500, 15000, 20),
            ("Laptop - ThinkPad T14", "Hardware", 3, 650000, 850000, 2),
            ("UPS Battery Backup", "Hardware", 5, 85000, 120000, 2),
            ("Internet Bandwidth (Gbps)", "Infrastructure", 1, 180000, 250000, 1),
            ("Cybersecurity Audit Package", "Services", 10, 200000, 750000, 3),
            ("Cloud Migration Package", "Services", 5, 500000, 1800000, 2),
            ("Monthly Support Retainer", "Services", 8, 150000, 350000, 3),
        ],
        "rev_categories": ["Software Development", "IT Consulting", "Support Contract", "Cloud Migration", "Cybersecurity Audit", "API Integration", "Data Analytics"],
        "exp_categories": ["Staff Salary", "Cloud Infrastructure", "Office Rent", "Internet", "Equipment", "Training", "Contract Developers", "Software Licenses"],
        "rev_range": (150000, 2500000),
        "exp_range": (50000, 800000),
        "daily_rev_count": (1, 3),
        "daily_exp_count": (1, 2),
        "nsi_base": 71,
        "alerts": [
            ("overdue_payment", "critical", "First Bank: N1.8M Invoice Overdue", "Project milestone delivered 30 days ago. Payment terms were net-15.", "Escalate to relationship manager and send formal demand"),
            ("cashflow_warning", "warning", "Salary Week: N3.2M Due Friday", "Staff salaries due in 4 days. Current balance is N2.1M with N1.5M receivables pending.", "Follow up on Flutterwave and Paystack invoices"),
            ("expense_spike", "info", "AWS Costs Up 25% This Month", "Cloud spend increased from N360,000 to N450,000. New client onboarding drove usage.", "Review resource allocation and consider reserved instances"),
            ("opportunity", "info", "Dangote Group RFP: N15M Contract", "Request for proposal received for enterprise IT infrastructure upgrade. Deadline in 10 days.", "Assign senior architect to prepare proposal by Thursday"),
            ("overdue_payment", "warning", "Interswitch: N2.4M Partial Payment", "Received N1.2M of N3.6M. Remaining N2.4M was due 7 days ago.", "Send statement of account and schedule call with CFO"),
        ],
        "signals": [
            ("invoice", {"vendor_name": "AWS Nigeria (via Flutterwave)", "invoice_id": "INV-2026-2001", "amount": 890000.00, "currency": "NGN", "due_date": 5, "description": "Cloud hosting and compute — March 2026"}),
            ("invoice", {"vendor_name": "Andela Talent Services", "invoice_id": "INV-2026-2002", "amount": 3500000.00, "currency": "NGN", "due_date": -7, "description": "Contract developer staffing — 2 senior engineers"}),
            ("invoice", {"vendor_name": "MainOne Data Centre", "invoice_id": "INV-2026-2003", "amount": 420000.00, "currency": "NGN", "due_date": 15, "description": "Colocation and bandwidth — Q1 2026"}),
            ("invoice", {"vendor_name": "Google Workspace Reseller", "invoice_id": "INV-2026-2004", "amount": 165000.00, "currency": "NGN", "due_date": 3, "description": "Google Workspace Business Plus — 25 seats"}),
            ("invoice", {"vendor_name": "Interswitch Payment Gateway", "invoice_id": "INV-2026-2005", "amount": 285000.00, "currency": "NGN", "due_date": -2, "description": "Payment processing fees — February"}),
            ("email", {"sender": "cto@fintechstartup.ng", "subject": "RFP: Mobile Banking App Development", "classification": "customer_inquiry", "body": "Looking for a dev partner to build our mobile banking platform. Budget is NGN 25M."}),
            ("email", {"sender": "billing@andela.com", "subject": "Urgent: Invoice INV-2026-2002 Past Due", "classification": "payment_reminder", "body": "Invoice for NGN 3,500,000 is now 7 days overdue. Please arrange payment."}),
            ("email", {"sender": "hr@techbridge.ng", "subject": "Staff Attrition Alert: 2 Resignations", "classification": "operational_message", "body": "Two mid-level developers resigned. Team capacity at 70%. Recommend urgent hiring."}),
            ("email", {"sender": "procurement@dangote.com", "subject": "IT Infrastructure Upgrade RFP", "classification": "customer_inquiry", "body": "Dangote Group is seeking proposals for enterprise IT infrastructure modernisation. Budget: NGN 15M."}),
            ("email", {"sender": "cfo@gtbank.com", "subject": "Q2 Support Contract Renewal", "classification": "customer_inquiry", "body": "We would like to renew our IT support contract for Q2. Please send updated pricing."}),
        ],
    },
    "ghana@demo.com": {
        "name": "Asante Fresh Market",
        "type": "supermarket",
        "country": "GH",
        "currency": "GHS",
        "tier": "growth",
        "suppliers": [
            ("Accra Wholesale Depot", "+233241111111"),
            ("Tema Fishing Co", "+233242222222"),
            ("Kumasi Grain Traders", "+233243333333"),
        ],
        "customers": [
            ("Osu Night Market", "+233244444444"),
            ("Labadi Catering", "+233245555555"),
            ("East Legon Homes", "+233246666666"),
        ],
        "products": [
            ("Tilapia (Fresh kg)", "Seafood", 80, 35, 55, 30),
            ("Gari (50kg bag)", "Grains", 25, 180, 250, 10),
            ("Palm Oil (25L)", "Oil", 15, 220, 320, 5),
            ("Plantain (Bunch)", "Produce", 60, 15, 25, 20),
            ("Yam (Tubers)", "Produce", 40, 20, 35, 15),
            ("Kenkey (Wrapped)", "Prepared", 100, 5, 10, 40),
        ],
        "rev_categories": ["Market Sales", "Wholesale", "Catering Orders", "Walk-in"],
        "exp_categories": ["Stock Purchase", "Rent", "Transport", "Staff Wages", "Utilities"],
        "rev_range": (500, 8000),
        "exp_range": (200, 5000),
        "daily_rev_count": (4, 8),
        "daily_exp_count": (1, 3),
        "nsi_base": 58,
        "alerts": [
            ("low_stock", "warning", "Tilapia stock dropping fast", "80kg remaining but daily sales average 15kg. Stockout in ~5 days.", "Order from Tema Fishing Co — 100kg batch"),
            ("overdue_payment", "warning", "Labadi Catering owes GHS 2,400", "Catering order delivered 10 days ago, payment pending.", "Send WhatsApp reminder to Labadi Catering"),
            ("expense_spike", "info", "Utility bills up 20%", "ECG electricity charges increased this quarter.", "Consider solar backup for cold storage"),
        ],
        "signals": [
            ("invoice", {"vendor_name": "Accra Wholesale Depot", "invoice_id": "INV-GH-0001", "amount": 12500.00, "currency": "GHS", "due_date": 7, "description": "Weekly produce restock — grains and oil"}),
            ("invoice", {"vendor_name": "Tema Fishing Co", "invoice_id": "INV-GH-0002", "amount": 4200.00, "currency": "GHS", "due_date": -2, "description": "Fresh tilapia — 120kg delivery"}),
            ("email", {"sender": "orders@labadi-catering.gh", "subject": "Bulk Order: 200 Kenkey + Tilapia", "classification": "customer_inquiry", "body": "We need 200 wrapped kenkey and 50kg tilapia for a weekend event. Please confirm."}),
            ("email", {"sender": "accounts@accrawholesale.gh", "subject": "Payment Due: INV-GH-0001", "classification": "payment_reminder", "body": "Your invoice for GHS 12,500 is due in 7 days."}),
        ],
    },
    "kenya@demo.com": {
        "name": "Mwangi Auto Garage",
        "type": "auto_mechanic",
        "country": "KE",
        "currency": "KES",
        "tier": "business",
        "suppliers": [
            ("Nairobi Auto Parts", "+254711111111"),
            ("Toyota Kenya", "+254722222222"),
            ("Shell Lubricants", "+254733333333"),
        ],
        "customers": [
            ("Safari Tours Ltd", "+254744444444"),
            ("Westlands Taxi Co", "+254755555555"),
            ("Karen Residents Assoc", "+254766666666"),
            ("Uber Kenya Drivers", "+254777777777"),
        ],
        "products": [
            ("Engine Oil 5W-30 (5L)", "Lubricants", 30, 2500, 3800, 10),
            ("Brake Pads (Set)", "Parts", 20, 3500, 6000, 8),
            ("Air Filter (Universal)", "Parts", 25, 800, 1500, 10),
            ("Car Battery 75Ah", "Electrical", 8, 12000, 18000, 3),
            ("Tyre 195/65R15", "Tyres", 12, 8500, 13000, 4),
        ],
        "rev_categories": ["Vehicle Repair", "Oil Change", "Tyre Service", "Engine Overhaul", "Diagnostics"],
        "exp_categories": ["Spare Parts", "Workshop Rent", "Mechanic Wages", "Tools", "Electricity"],
        "rev_range": (5000, 85000),
        "exp_range": (3000, 45000),
        "daily_rev_count": (2, 5),
        "daily_exp_count": (1, 2),
        "nsi_base": 66,
        "alerts": [
            ("low_stock", "warning", "Car Batteries Running Low", "Only 8 units left. Average 3 sold per week.", "Order 15 units from Nairobi Auto Parts"),
            ("overdue_payment", "critical", "Safari Tours: KES 125,000 Overdue", "Fleet service completed 3 weeks ago. Payment terms were 14 days.", "Call fleet manager and send invoice reminder"),
            ("cashflow_warning", "warning", "Rent Due: KES 80,000 in 5 Days", "Workshop rent due soon. Current balance KES 62,000.", "Collect pending payments from Westlands Taxi Co"),
        ],
        "signals": [
            ("invoice", {"vendor_name": "Nairobi Auto Parts", "invoice_id": "INV-KE-0001", "amount": 185000.00, "currency": "KES", "due_date": 10, "description": "Brake pads, filters, and batteries — monthly restock"}),
            ("invoice", {"vendor_name": "Shell Lubricants", "invoice_id": "INV-KE-0002", "amount": 75000.00, "currency": "KES", "due_date": -5, "description": "Engine oil and transmission fluid"}),
            ("email", {"sender": "fleet@safaritours.ke", "subject": "Service 8 Vehicles Next Week", "classification": "customer_inquiry", "body": "We need full service for 8 Land Cruisers. Please schedule and quote."}),
            ("email", {"sender": "accounts@nairobiparts.ke", "subject": "Overdue: INV-KE-0002", "classification": "payment_reminder", "body": "Your invoice for KES 75,000 is 5 days overdue."}),
        ],
    },
    "southafrica@demo.com": {
        "name": "Ndlovu Fashion House",
        "type": "fashion_textile",
        "country": "ZA",
        "currency": "ZAR",
        "tier": "growth",
        "suppliers": [
            ("Cape Town Fabrics", "+27821111111"),
            ("Durban Thread Co", "+27822222222"),
            ("Joburg Buttons & Zips", "+27823333333"),
        ],
        "customers": [
            ("Sandton City Boutique", "+27824444444"),
            ("Soweto Fashion Week", "+27825555555"),
            ("Online Store Orders", "+27826666666"),
        ],
        "products": [
            ("Ankara Fabric (6 yards)", "Fabric", 50, 350, 650, 15),
            ("Lace Material (5 yards)", "Fabric", 30, 800, 1500, 10),
            ("Ready-made Dress", "Clothing", 15, 400, 1200, 5),
            ("Tailored Suit", "Clothing", 8, 1200, 3500, 3),
            ("Accessories Pack", "Accessories", 40, 80, 250, 15),
        ],
        "rev_categories": ["Clothing Sales", "Fabric Sales", "Custom Tailoring", "Online Orders"],
        "exp_categories": ["Fabric Purchase", "Tailor Wages", "Shop Rent", "Marketing", "Utilities"],
        "rev_range": (2000, 35000),
        "exp_range": (1000, 15000),
        "daily_rev_count": (2, 5),
        "daily_exp_count": (1, 2),
        "nsi_base": 52,
        "alerts": [
            ("low_stock", "warning", "Ankara Fabric Running Low", "50 pieces left but Soweto Fashion Week orders expected next week.", "Order 100 pieces from Cape Town Fabrics"),
            ("seasonal_risk", "info", "Fashion Week Season Approaching", "Soweto Fashion Week in 4 weeks. Historically 3x normal orders.", "Pre-order fabrics and hire 2 temporary tailors"),
            ("overdue_payment", "warning", "Sandton City Boutique: R8,500 Overdue", "Consignment delivered 18 days ago.", "Follow up with store manager"),
        ],
        "signals": [
            ("invoice", {"vendor_name": "Cape Town Fabrics", "invoice_id": "INV-ZA-0001", "amount": 28500.00, "currency": "ZAR", "due_date": 14, "description": "Ankara and lace fabric — bulk order"}),
            ("invoice", {"vendor_name": "Durban Thread Co", "invoice_id": "INV-ZA-0002", "amount": 4200.00, "currency": "ZAR", "due_date": 7, "description": "Thread, needles, and sewing supplies"}),
            ("email", {"sender": "events@sowetofashion.za", "subject": "Fashion Week Vendor Registration", "classification": "customer_inquiry", "body": "Register as a vendor for Soweto Fashion Week 2026. Booth fee R5,000. Expected footfall: 15,000."}),
            ("email", {"sender": "orders@sandtoncity.za", "subject": "Restock Request: 20 Dresses", "classification": "customer_inquiry", "body": "Your dresses are selling well. Please deliver 20 more units by Friday."}),
        ],
    },
    "rwanda@demo.com": {
        "name": "Kigali Pharmacy Plus",
        "type": "pharmacy",
        "country": "RW",
        "currency": "RWF",
        "tier": "starter",
        "suppliers": [
            ("Rwanda Pharma Distributors", "+250781111111"),
            ("Kigali Medical Supplies", "+250782222222"),
        ],
        "customers": [
            ("Nyarugenge Health Centre", "+250783333333"),
            ("Walk-in Patients", "+250784444444"),
        ],
        "products": [
            ("Paracetamol 500mg (Box 100)", "Pain Relief", 200, 2500, 4000, 50),
            ("Amoxicillin 250mg (Box 30)", "Antibiotics", 80, 5000, 8500, 20),
            ("Oral Rehydration Salts (Box 50)", "ORS", 60, 3000, 5000, 15),
            ("Malaria Test Kit (Box 25)", "Diagnostics", 30, 12000, 20000, 10),
            ("Hand Sanitizer 500ml", "Hygiene", 45, 1500, 3000, 15),
        ],
        "rev_categories": ["Prescription Sales", "OTC Sales", "Health Supplies", "Diagnostics"],
        "exp_categories": ["Medicine Stock", "Pharmacist Salary", "Rent", "Utilities", "Licensing"],
        "rev_range": (15000, 120000),
        "exp_range": (10000, 80000),
        "daily_rev_count": (3, 7),
        "daily_exp_count": (1, 2),
        "nsi_base": 48,
        "alerts": [
            ("low_stock", "critical", "Amoxicillin Stock Critical", "Only 80 boxes left. Average daily sales: 8 boxes. Stockout in 10 days.", "Emergency order from Rwanda Pharma Distributors"),
            ("regulatory", "warning", "Pharmacy License Renewal Due", "License expires in 30 days. Renewal process takes 2 weeks.", "Start renewal application immediately"),
            ("expense_spike", "info", "Medicine costs up 12%", "Supplier price increases on antibiotics and diagnostics.", "Negotiate bulk pricing or find alternative suppliers"),
        ],
        "signals": [
            ("invoice", {"vendor_name": "Rwanda Pharma Distributors", "invoice_id": "INV-RW-0001", "amount": 850000.00, "currency": "RWF", "due_date": 14, "description": "Monthly medicine restock — antibiotics and pain relief"}),
            ("invoice", {"vendor_name": "Kigali Medical Supplies", "invoice_id": "INV-RW-0002", "amount": 360000.00, "currency": "RWF", "due_date": 7, "description": "Diagnostic kits and hygiene products"}),
            ("email", {"sender": "procurement@nyarugenge.rw", "subject": "Monthly Supply Request", "classification": "customer_inquiry", "body": "We need 50 boxes paracetamol and 20 boxes amoxicillin for the health centre."}),
        ],
    },
    "uk@demo.com": {
        "name": "Thames Valley Plumbing",
        "type": "construction",
        "country": "GB",
        "currency": "GBP",
        "tier": "business",
        "suppliers": [
            ("Screwfix Trade Account", "+447911111111"),
            ("Vaillant Boilers UK", "+447922222222"),
            ("Toolstation", "+447933333333"),
        ],
        "customers": [
            ("Oxford Property Lettings", "+447944444444"),
            ("Reading Borough Council", "+447955555555"),
            ("Henley Homes Ltd", "+447966666666"),
            ("Private Clients", "+447977777777"),
        ],
        "products": [
            ("Copper Pipe 15mm (3m)", "Plumbing", 50, 8, 15, 20),
            ("Combi Boiler Vaillant", "Heating", 3, 1200, 2800, 1),
            ("Bathroom Tap Set", "Fixtures", 12, 45, 120, 5),
            ("Pipe Fittings Assorted", "Plumbing", 200, 2, 5, 50),
            ("Silicone Sealant (Box 12)", "Consumables", 8, 36, 0, 3),
        ],
        "rev_categories": ["Plumbing Repair", "Boiler Install", "Bathroom Fit", "Emergency Callout", "Maintenance Contract"],
        "exp_categories": ["Materials", "Van Fuel", "Insurance", "Apprentice Wages", "Tools", "Advertising"],
        "rev_range": (200, 4500),
        "exp_range": (50, 1500),
        "daily_rev_count": (1, 4),
        "daily_exp_count": (1, 3),
        "nsi_base": 74,
        "alerts": [
            ("overdue_payment", "warning", "Reading Council: £3,200 Overdue", "Emergency repair job completed 28 days ago. Council payment terms are 30 days.", "Submit follow-up invoice to accounts payable"),
            ("low_stock", "info", "Combi Boilers: Only 3 Left", "Winter season approaching — boiler installs typically double.", "Order 5 units from Vaillant at trade discount"),
            ("regulatory", "warning", "Gas Safe Cert Expiring — Jake", "Apprentice certification expires in 3 weeks.", "Book renewal course immediately"),
        ],
        "signals": [
            ("invoice", {"vendor_name": "Screwfix Trade Account", "invoice_id": "INV-UK-0001", "amount": 1340.00, "currency": "GBP", "due_date": 10, "description": "Copper pipe, fittings, and sealant — monthly stock"}),
            ("invoice", {"vendor_name": "Vaillant Boilers UK", "invoice_id": "INV-UK-0002", "amount": 4200.00, "currency": "GBP", "due_date": -6, "description": "3x combi boiler units for customer installs"}),
            ("email", {"sender": "lettings@oxfordproperty.co.uk", "subject": "Ongoing Contract: 12 Properties", "classification": "customer_inquiry", "body": "We manage 12 rental properties and need a reliable plumber on retainer. 12-month contract."}),
            ("email", {"sender": "trade@vaillant.co.uk", "subject": "Overdue: INV-UK-0002", "classification": "payment_reminder", "body": "Invoice for GBP 4,200 is 6 days past due. Late payment may affect trade discount."}),
            ("email", {"sender": "council@reading.gov.uk", "subject": "New Tender: Social Housing Plumbing", "classification": "customer_inquiry", "body": "Tender for plumbing maintenance across 45 council properties. Deadline: April 15."}),
        ],
    },
}


# ═══════════════════════════════════════════════════════════════
# SEEDING FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def seed_business_record(org_id, biz):
    """Seed the businesses table with rich metadata.
    
    Note: businesses table uses business_id as partition key per setup-aws.sh.
    We set business_id = org_id (they are the same value).
    """
    businesses_table.put_item(Item={
        "business_id": org_id,
        "org_id": org_id,
        "business_name": biz["name"],
        "business_type": biz["type"],
        "country": biz["country"],
        "currency": biz["currency"],
        "pricing_tier": biz["tier"],
        "onboarding_complete": True,
        "created_at": iso(now - timedelta(days=45)),
    })


def seed_counterparties(org_id, biz):
    """Seed suppliers and customers."""
    for name, phone in biz["suppliers"]:
        cp_table.put_item(Item={
            "org_id": org_id, "business_id": org_id,
            "counterparty_id": _id("counterparty"),
            "name": name, "counterparty_type": "supplier", "phone": phone,
            "balance_owed": dec(random.uniform(0, 150000)),
            "balance_owing": dec(0),
            "created_at": iso(now - timedelta(days=random.randint(10, 40))),
        })
    for name, phone in biz["customers"]:
        cp_table.put_item(Item={
            "org_id": org_id, "business_id": org_id,
            "counterparty_id": _id("counterparty"),
            "name": name, "counterparty_type": "customer", "phone": phone,
            "balance_owed": dec(0),
            "balance_owing": dec(random.uniform(0, 80000)),
            "created_at": iso(now - timedelta(days=random.randint(10, 40))),
        })


def seed_inventory(org_id, biz):
    """Seed inventory items."""
    for name, cat, qty, cost, price, reorder in biz["products"]:
        inv_table.put_item(Item={
            "org_id": org_id, "business_id": org_id,
            "item_id": _id("inventory_item"),
            "name": name, "category": cat,
            "quantity_on_hand": dec(qty), "unit": "units",
            "unit_cost": dec(cost),
            "selling_price": dec(price) if price > 0 else None,
            "reorder_point": dec(reorder),
            "created_at": iso(now - timedelta(days=30)),
            "last_updated": iso(now - timedelta(days=random.randint(0, 5))),
        })


def seed_transactions(org_id, biz):
    """Seed 30 days of transactions."""
    rev_lo, rev_hi = biz["rev_range"]
    exp_lo, exp_hi = biz["exp_range"]
    customer_names = [c[0] for c in biz["customers"]] + ["Walk-in"]
    supplier_names = [s[0] for s in biz["suppliers"]] + ["Staff", "Landlord"]

    for day_offset in range(30):
        dt = now - timedelta(days=day_offset)
        # Revenue
        rev_lo_count, rev_hi_count = biz["daily_rev_count"]
        for _ in range(random.randint(rev_lo_count, rev_hi_count)):
            txn_table.put_item(Item={
                "org_id": org_id, "transaction_id": _id("transaction"),
                "business_id": org_id,
                "transaction_type": "revenue",
                "category": random.choice(biz["rev_categories"]),
                "amount": dec(random.uniform(rev_lo, rev_hi)),
                "currency": biz["currency"],
                "counterparty_name": random.choice(customer_names),
                "description": f"Daily sales — {random.choice(['morning', 'afternoon', 'evening'])}",
                "date": iso(dt),
                "payment_status": random.choice(["paid", "paid", "paid", "pending"]),
                "created_at": iso(dt),
            })
        # Expenses
        exp_lo_count, exp_hi_count = biz["daily_exp_count"]
        for _ in range(random.randint(exp_lo_count, exp_hi_count)):
            txn_table.put_item(Item={
                "org_id": org_id, "transaction_id": _id("transaction"),
                "business_id": org_id,
                "transaction_type": "expense",
                "category": random.choice(biz["exp_categories"]),
                "amount": dec(random.uniform(exp_lo, exp_hi)),
                "currency": biz["currency"],
                "counterparty_name": random.choice(supplier_names),
                "description": "Operating expense",
                "date": iso(dt),
                "payment_status": "paid",
                "created_at": iso(dt),
            })


def seed_alerts(org_id, biz):
    """Seed business alerts."""
    for alert_data in biz["alerts"]:
        atype, sev, title, desc, action = alert_data[0], alert_data[1], alert_data[2], alert_data[3], alert_data[4]
        alert_table.put_item(Item={
            "org_id": org_id, "business_id": org_id,
            "alert_id": _id("alert"),
            "alert_type": atype, "severity": sev,
            "title": title, "description": desc, "recommended_action": action,
            "is_read": False, "created_at": iso(now - timedelta(hours=random.randint(1, 72))),
        })


def seed_signals(org_id, biz):
    """Seed invoice and email signals."""
    for i, (sig_type, content) in enumerate(biz["signals"]):
        sig_content = {}
        for k, v in content.items():
            if isinstance(v, float):
                sig_content[k] = dec(v)
            elif k == "due_date" and isinstance(v, int):
                sig_content[k] = iso(now + timedelta(days=v))
            else:
                sig_content[k] = v
        signals_table.put_item(Item={
            "org_id": org_id, "signal_id": _id("signal"),
            "signal_type": sig_type,
            "processing_status": "processed",
            "content": sig_content,
            "created_at": iso(now - timedelta(days=random.randint(1, 14))),
        })


def seed_nsi_scores(org_id, biz):
    """Seed 7 days of NSI score history for trend charts.
    
    NSI table key: org_id (HASH) + nsi_id (RANGE).
    The DDB service also reads 'timestamp' for sorting, so we include both.
    """
    base = biz["nsi_base"]
    for day_offset in range(7):
        dt = now - timedelta(days=day_offset)
        jitter = random.uniform(-5, 5)
        nsi_val = max(10, min(95, base + jitter))
        liq = max(10, min(95, base + random.uniform(-10, 10)))
        rev = max(10, min(95, base + random.uniform(-8, 12)))
        ops = max(10, min(95, base + random.uniform(-12, 8)))
        ven = max(10, min(95, base + random.uniform(-15, 5)))

        risks = []
        if liq < 50:
            risks.append({"risk": "Cash flow pressure — outgoing exceeds incoming this week", "severity": "high"})
        if ven < 45:
            risks.append({"risk": "Over-reliance on single supplier for key inputs", "severity": "medium"})
        if ops < 50:
            risks.append({"risk": "Slow invoice processing — average 5 days to record", "severity": "medium"})
        if rev < 55:
            risks.append({"risk": "Revenue inconsistency — 30% variance week-over-week", "severity": "high"})
        if not risks:
            risks.append({"risk": "Minor: review upcoming payment deadlines", "severity": "low"})

        nid = _id("nsi")
        nsi_table.put_item(Item={
            "org_id": org_id,
            "nsi_id": nid,
            "timestamp": iso(dt),
            "nsi_score": dec(nsi_val),
            "nova_stability_index": dec(nsi_val),
            "liquidity_index": dec(liq),
            "revenue_stability_index": dec(rev),
            "operational_latency_index": dec(ops),
            "vendor_risk_index": dec(ven),
            "confidence": random.choice(["high", "medium"]),
            "top_risks": risks,
            "signal_count": random.randint(3, 12),
            "explanation": f"NSI calculated from {random.randint(5, 20)} signals. Business health is {'stable' if nsi_val >= 60 else 'needs attention'}.",
        })


def seed_strategies(org_id, biz):
    """Seed 3-5 strategies per business."""
    strategy_templates = [
        ("Negotiate bulk discount with top supplier to reduce COGS by 8%", 4.5, 0.72, True),
        ("Implement 7-day payment follow-up cycle for overdue receivables", 6.2, 0.81, True),
        ("Diversify supplier base — add 2 alternative vendors for key inputs", 3.8, 0.65, False),
        ("Launch WhatsApp ordering channel to increase walk-in conversion", 5.1, 0.58, False),
        ("Reduce transport costs by consolidating deliveries to 2x per week", 2.9, 0.74, True),
    ]
    nsi_id = _id("nsi")
    strategy_ids = []
    for desc, improvement, confidence, auto in random.sample(strategy_templates, min(4, len(strategy_templates))):
        sid = _id("strategy")
        strategy_ids.append(sid)
        strategies_table.put_item(Item={
            "org_id": org_id,
            "simulation_id": sid,
            "strategy_id": sid,
            "nsi_snapshot_id": nsi_id,
            "description": desc,
            "predicted_nsi_improvement": dec(improvement),
            "confidence_score": dec(confidence),
            "automation_eligibility": auto,
            "reasoning": f"Based on analysis of {random.randint(10, 30)} transactions and {random.randint(3, 8)} signals.",
            "created_at": iso(now - timedelta(days=random.randint(1, 7))),
        })
    return strategy_ids


def seed_actions(org_id, strategy_ids):
    """Seed executed actions linked to strategies."""
    action_types = ["send_payment_reminder", "generate_purchase_order", "schedule_follow_up", "flag_for_review", "auto_categorise_transactions"]
    targets = ["accounts_receivable", "supplier_orders", "cashflow_management", "inventory_reorder", "transaction_log"]
    execution_ids = []
    for i, sid in enumerate(strategy_ids[:3]):
        eid = _id("action")
        execution_ids.append((eid, sid))
        actions_table.put_item(Item={
            "org_id": org_id,
            "action_id": eid,
            "execution_id": eid,
            "strategy_id": sid,
            "action_type": action_types[i % len(action_types)],
            "target_entity": targets[i % len(targets)],
            "execution_status": random.choice(["success", "success", "success", "pending"]),
            "timestamp": iso(now - timedelta(days=random.randint(0, 5))),
        })
    return execution_ids


def seed_evaluations(org_id, execution_ids, biz):
    """Seed post-action evaluations."""
    base = biz["nsi_base"]
    for eid, sid in execution_ids:
        old_nsi = round(base + random.uniform(-3, 3), 2)
        improvement = round(random.uniform(0.5, 6.0), 2)
        new_nsi = round(min(95, old_nsi + improvement), 2)
        actual = round(new_nsi - old_nsi, 2)
        predicted = round(actual + random.uniform(-1.5, 1.5), 2)
        accuracy = round(max(0.3, min(1.0, 1.0 - abs(predicted - actual) / max(abs(predicted), 1))), 2)

        evaluations_table.put_item(Item={
            "org_id": org_id,
            "evaluation_id": _id("evaluation"),
            "execution_id": eid,
            "old_nsi": dec(old_nsi),
            "new_nsi": dec(new_nsi),
            "predicted_improvement": dec(predicted),
            "actual_improvement": dec(actual),
            "prediction_accuracy": dec(accuracy),
            "timestamp": iso(now - timedelta(days=random.randint(0, 3))),
        })


def seed_insights(org_id, biz):
    """Seed AI-generated business insights."""
    currency = biz["currency"]
    symbol = {"NGN": "₦", "GHS": "GH₵", "KES": "KES ", "ZAR": "R", "RWF": "RWF ", "GBP": "£"}.get(currency, currency + " ")

    insight_templates = [
        ("sales_trend", f"Revenue trending up 12% over last 14 days",
         f"Your daily average revenue increased from {symbol}{random.randint(20, 80):,}k to {symbol}{random.randint(85, 150):,}k. Consistent growth across top 3 product categories.",
         {"trend": "up", "percentage": 12, "period": "14d"}),
        ("profitable_product", f"Top margin product identified",
         f"Your highest-margin item generates {random.randint(35, 65)}% gross margin. Consider increasing stock levels and promoting it.",
         {"margin_pct": random.randint(35, 65), "recommendation": "increase_stock"}),
        ("cost_saving", f"Potential savings on recurring expenses",
         f"Transport/logistics costs could be reduced by {random.randint(10, 25)}% through route consolidation.",
         {"saving_pct": random.randint(10, 25), "category": "transport"}),
        ("cashflow", f"Cash flow forecast: next 7 days",
         f"Projected inflows: {symbol}{random.randint(100, 500):,}k. Projected outflows: {symbol}{random.randint(80, 400):,}k. Net positive but tight.",
         {"inflows": random.randint(100000, 500000), "outflows": random.randint(80000, 400000)}),
        ("inventory_risk", f"3 items approaching reorder point",
         f"Stock levels for 3 products will hit reorder point within 5 days at current sales velocity.",
         {"items_at_risk": 3, "days_to_stockout": 5}),
        ("customer_segmentation", f"Top customers drive 60% of revenue",
         f"Your top 3 customers account for 60% of total revenue. Consider loyalty incentives to retain them.",
         {"top_customer_share": 60, "recommendation": "loyalty_program"}),
    ]

    for itype, title, desc, data in insight_templates:
        insights_table.put_item(Item={
            "business_id": org_id,
            "org_id": org_id,
            "insight_id": _id("insight"),
            "insight_type": itype,
            "title": title,
            "description": desc,
            "data": data,
            "created_at": iso(now - timedelta(hours=random.randint(1, 48))),
        })


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def seed_one_business(email, biz):
    """Seed all data for a single business account."""
    org_id = get_org_id(email)
    if not org_id:
        return

    print(f"\n  [{biz['country']}] {biz['name']} ({email}) — org: {org_id}")

    seed_business_record(org_id, biz)
    print(f"    [OK] Business record")

    seed_counterparties(org_id, biz)
    print(f"    [OK] {len(biz['suppliers'])} suppliers + {len(biz['customers'])} customers")

    seed_inventory(org_id, biz)
    print(f"    [OK] {len(biz['products'])} inventory items")

    seed_transactions(org_id, biz)
    print(f"    [OK] 30 days of transactions")

    seed_alerts(org_id, biz)
    print(f"    [OK] {len(biz['alerts'])} alerts")

    seed_signals(org_id, biz)
    print(f"    [OK] {len(biz['signals'])} signals (invoices + emails)")

    seed_nsi_scores(org_id, biz)
    print(f"    [OK] 7 days of NSI scores")

    strategy_ids = seed_strategies(org_id, biz)
    print(f"    [OK] {len(strategy_ids)} strategies")

    execution_ids = seed_actions(org_id, strategy_ids)
    print(f"    [OK] {len(execution_ids)} actions")

    seed_evaluations(org_id, execution_ids, biz)
    print(f"    [OK] {len(execution_ids)} evaluations")

    seed_insights(org_id, biz)
    print(f"    [OK] 6 AI insights")


if __name__ == "__main__":
    print("=" * 60)
    print("  Enriched Data Seeder — All Businesses, All Tables")
    print("=" * 60)

    for email, biz in BUSINESSES.items():
        try:
            seed_one_business(email, biz)
        except Exception as e:
            print(f"  ERROR seeding {email}: {e}")

    print("\n" + "=" * 60)
    print("  Done! All dashboards should now have data.")
    print("=" * 60)
    print("\n--- Test Accounts ---")
    print(f"{'Email':<30} {'Password':<15} {'Tier':<12} {'Country':<5} {'Business'}")
    print("-" * 100)
    for email, biz in BUSINESSES.items():
        print(f"{email:<30} {'Demo@2025!':<15} {biz['tier']:<12} {biz['country']:<5} {biz['name']}")
    print(f"{'admin@smecontroltower.com':<30} {'Admin@2025!':<15} {'enterprise':<12} {'NG':<5} SME Control Tower")
