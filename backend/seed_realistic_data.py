"""
Seed realistic Nigerian SME transaction data for all test accounts.

Usage:
  python seed_realistic_data.py

Seeds transactions, inventory, counterparties, and alerts for:
  - Ade's Trading Co (starter) — retail/distribution
  - GreenField Farms (growth) — agriculture
  - TechBridge Solutions (business) — IT services
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

txn_table = ddb.Table(settings.transactions_table)
inv_table = ddb.Table(settings.inventory_table)
cp_table = ddb.Table(settings.counterparties_table)
alert_table = ddb.Table(settings.alerts_table)

# Get org_ids from users table
users_table = ddb.Table(settings.users_table)


def get_org_id(email):
    resp = users_table.get_item(Key={"email": email})
    return resp["Item"]["org_id"]


def _id(entity: str) -> str:
    return generate_id(entity)


def dec(v):
    return Decimal(str(round(v, 2)))


def iso(dt):
    return dt.isoformat()


now = datetime.now(timezone.utc)


def seed_ades_trading(org_id):
    """Ade's Trading Co — Lagos retail/distribution. Sells FMCG, provisions, drinks."""
    print(f"  Seeding Ade's Trading Co ({org_id})...")

    # Counterparties
    suppliers = [
        ("Dangote Industries", "supplier", "+2348012345678"),
        ("Nigerian Breweries", "supplier", "+2348023456789"),
        ("Unilever Nigeria", "supplier", "+2348034567890"),
        ("PZ Cussons", "supplier", "+2348045678901"),
        ("Nestle Nigeria", "supplier", "+2348056789012"),
    ]
    customers = [
        ("Mama Nkechi Shop", "customer", "+2348067890123"),
        ("Ikeja Mini Mart", "customer", "+2348078901234"),
        ("Surulere Provisions", "customer", "+2348089012345"),
    ]
    for name, ctype, phone in suppliers + customers:
        cp_table.put_item(Item={
            "org_id": org_id, "counterparty_id": _id("counterparty"),
            "name": name, "counterparty_type": ctype, "phone": phone,
            "balance_owed": dec(random.uniform(0, 150000) if ctype == "supplier" else 0),
            "balance_owing": dec(random.uniform(0, 80000) if ctype == "customer" else 0),
            "created_at": iso(now),
        })

    # Inventory — FMCG products
    products = [
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
    ]
    for name, cat, qty, cost, price, reorder in products:
        inv_table.put_item(Item={
            "org_id": org_id, "item_id": _id("inventory_item"),
            "name": name, "category": cat,
            "quantity_on_hand": dec(qty), "unit": "units",
            "unit_cost": dec(cost), "selling_price": dec(price),
            "reorder_point": dec(reorder),
            "created_at": iso(now), "last_updated": iso(now),
        })

    # Transactions — 30 days of daily sales and expenses
    categories_rev = ["Provisions Sales", "Beverages Sales", "Wholesale Order", "Walk-in Customer"]
    categories_exp = ["Stock Purchase", "Rent", "Transport/Logistics", "Staff Salary", "Electricity", "Phone/Data"]
    for day_offset in range(30):
        dt = now - timedelta(days=day_offset)
        # 3-6 revenue transactions per day
        for _ in range(random.randint(3, 6)):
            txn_table.put_item(Item={
                "org_id": org_id, "transaction_id": _id("transaction"),
                "business_id": org_id,
                "transaction_type": "revenue",
                "category": random.choice(categories_rev),
                "amount": dec(random.uniform(5000, 85000)),
                "currency": "NGN",
                "counterparty_name": random.choice(["Mama Nkechi Shop", "Ikeja Mini Mart", "Walk-in", "Surulere Provisions"]),
                "description": f"Daily sales - {random.choice(['morning','afternoon','evening'])}",
                "date": iso(dt), "payment_status": random.choice(["paid", "paid", "paid", "pending"]),
                "created_at": iso(dt),
            })
        # 1-2 expense transactions per day
        for _ in range(random.randint(1, 2)):
            cat = random.choice(categories_exp)
            amt = {
                "Stock Purchase": random.uniform(50000, 350000),
                "Rent": 150000 if day_offset == 0 else 0,
                "Transport/Logistics": random.uniform(3000, 15000),
                "Staff Salary": 85000 if day_offset == 0 else 0,
                "Electricity": random.uniform(5000, 20000),
                "Phone/Data": random.uniform(1000, 5000),
            }.get(cat, random.uniform(5000, 30000))
            if amt > 0:
                txn_table.put_item(Item={
                    "org_id": org_id, "transaction_id": _id("transaction"),
                    "business_id": org_id,
                    "transaction_type": "expense",
                    "category": cat,
                    "amount": dec(amt),
                    "currency": "NGN",
                    "counterparty_name": random.choice(["Dangote Industries", "Nigerian Breweries", "IKEDC", "Staff"]),
                    "description": f"{cat} payment",
                    "date": iso(dt), "payment_status": "paid",
                    "created_at": iso(dt),
                })

    # Alerts
    alerts_data = [
        ("low_stock", "warning", "Low Stock: Dangote Sugar 50kg", "Only 18 bags remaining. Reorder point is 8 but sales velocity suggests stockout in 5 days.", "Place order with Dangote Industries for 30 bags"),
        ("cashflow_warning", "critical", "Cash Flow Pressure This Week", "Outgoing payments of ₦485,000 due but projected revenue is ₦320,000.", "Delay non-urgent stock purchases or collect outstanding receivables"),
        ("overdue_payment", "warning", "Overdue: Ikeja Mini Mart owes ₦67,500", "Invoice from 14 days ago still unpaid. Customer usually pays within 7 days.", "Send payment reminder via WhatsApp"),
    ]
    for atype, sev, title, desc, action in alerts_data:
        alert_table.put_item(Item={
            "org_id": org_id, "alert_id": _id("alert"),
            "business_id": org_id, "alert_type": atype, "severity": sev,
            "title": title, "description": desc, "recommended_action": action,
            "is_read": False, "created_at": iso(now),
        })


def seed_greenfield_farms(org_id):
    """GreenField Farms — Ogun State agriculture. Grows cassava, maize, vegetables."""
    print(f"  Seeding GreenField Farms ({org_id})...")

    suppliers = [
        ("Agro-Allied Chemicals", "supplier", "+2348112345678"),
        ("Tractor Hire Services", "supplier", "+2348123456789"),
        ("Seed Nigeria Ltd", "supplier", "+2348134567890"),
    ]
    customers = [
        ("Lagos Garri Factory", "customer", "+2348145678901"),
        ("Sango Market Traders", "customer", "+2348156789012"),
        ("FoodCo Supermarket", "customer", "+2348167890123"),
        ("Shoprite Nigeria", "customer", "+2348178901234"),
    ]
    for name, ctype, phone in suppliers + customers:
        cp_table.put_item(Item={
            "org_id": org_id, "counterparty_id": _id("counterparty"),
            "name": name, "counterparty_type": ctype, "phone": phone,
            "balance_owed": dec(random.uniform(0, 200000) if ctype == "supplier" else 0),
            "balance_owing": dec(random.uniform(0, 300000) if ctype == "customer" else 0),
            "created_at": iso(now),
        })

    products = [
        ("Cassava (Tonnes)", "Root Crops", 12, 85000, 120000, 5),
        ("Maize (Bags 100kg)", "Grains", 45, 28000, 38000, 15),
        ("Tomatoes (Baskets)", "Vegetables", 30, 8000, 15000, 10),
        ("Pepper (Bags)", "Vegetables", 25, 12000, 22000, 8),
        ("Palm Oil (25L Jerrycans)", "Oil", 20, 18000, 28000, 8),
        ("Fertilizer NPK (Bags)", "Inputs", 35, 15000, 0, 10),
        ("Herbicide (Litres)", "Inputs", 50, 3500, 0, 15),
    ]
    for name, cat, qty, cost, price, reorder in products:
        inv_table.put_item(Item={
            "org_id": org_id, "item_id": _id("inventory_item"),
            "name": name, "category": cat,
            "quantity_on_hand": dec(qty), "unit": "units",
            "unit_cost": dec(cost), "selling_price": dec(price) if price > 0 else None,
            "reorder_point": dec(reorder),
            "created_at": iso(now), "last_updated": iso(now),
        })

    # Transactions — seasonal agriculture pattern
    for day_offset in range(30):
        dt = now - timedelta(days=day_offset)
        # Revenue: 1-3 sales per day (harvest season)
        for _ in range(random.randint(1, 3)):
            txn_table.put_item(Item={
                "org_id": org_id, "transaction_id": _id("transaction"),
                "business_id": org_id,
                "transaction_type": "revenue",
                "category": random.choice(["Cassava Sales", "Maize Sales", "Vegetable Sales", "Palm Oil Sales"]),
                "amount": dec(random.uniform(25000, 250000)),
                "currency": "NGN",
                "counterparty_name": random.choice(["Lagos Garri Factory", "Sango Market Traders", "FoodCo Supermarket", "Shoprite Nigeria"]),
                "description": "Farm produce delivery",
                "date": iso(dt), "payment_status": random.choice(["paid", "paid", "pending"]),
                "created_at": iso(dt),
            })
        # Expenses
        if random.random() > 0.4:
            txn_table.put_item(Item={
                "org_id": org_id, "transaction_id": _id("transaction"),
                "business_id": org_id,
                "transaction_type": "expense",
                "category": random.choice(["Farm Labour", "Fertilizer", "Transport", "Equipment Hire", "Diesel/Fuel"]),
                "amount": dec(random.uniform(10000, 120000)),
                "currency": "NGN",
                "counterparty_name": random.choice(["Farm Workers", "Agro-Allied Chemicals", "Tractor Hire Services"]),
                "description": "Farm operations expense",
                "date": iso(dt), "payment_status": "paid",
                "created_at": iso(dt),
            })

    alerts_data = [
        ("low_stock", "warning", "Fertilizer Running Low", "Only 35 bags of NPK remaining. Next planting season starts in 3 weeks.", "Order 50 bags from Agro-Allied Chemicals"),
        ("overdue_payment", "critical", "FoodCo Supermarket: ₦180,000 Overdue", "Delivery made 21 days ago, payment terms were 14 days.", "Call procurement manager and send formal reminder"),
        ("expense_spike", "info", "Transport Costs Up 40%", "Fuel price increase has pushed logistics costs from ₦45,000 to ₦63,000 per week.", "Consider bulk transport scheduling to reduce trips"),
    ]
    for atype, sev, title, desc, action in alerts_data:
        alert_table.put_item(Item={
            "org_id": org_id, "alert_id": _id("alert"),
            "business_id": org_id, "alert_type": atype, "severity": sev,
            "title": title, "description": desc, "recommended_action": action,
            "is_read": False, "created_at": iso(now),
        })


def seed_techbridge(org_id):
    """TechBridge Solutions — Lagos IT services. Software dev, consulting, support."""
    print(f"  Seeding TechBridge Solutions ({org_id})...")

    suppliers = [
        ("AWS Nigeria", "supplier", "+2348212345678"),
        ("Konga Office Supplies", "supplier", "+2348223456789"),
        ("MainOne Internet", "supplier", "+2348234567890"),
    ]
    customers = [
        ("First Bank Nigeria", "customer", "+2348245678901"),
        ("GTBank", "customer", "+2348256789012"),
        ("Flutterwave", "customer", "+2348267890123"),
        ("Paystack", "customer", "+2348278901234"),
        ("Interswitch", "customer", "+2348289012345"),
        ("Sterling Bank", "customer", "+2348290123456"),
    ]
    for name, ctype, phone in suppliers + customers:
        cp_table.put_item(Item={
            "org_id": org_id, "counterparty_id": _id("counterparty"),
            "name": name, "counterparty_type": ctype, "phone": phone,
            "balance_owed": dec(random.uniform(0, 500000) if ctype == "supplier" else 0),
            "balance_owing": dec(random.uniform(0, 2000000) if ctype == "customer" else 0),
            "created_at": iso(now),
        })

    # IT services don't have traditional inventory, but track project hours/licenses
    products = [
        ("AWS Credits (Monthly)", "Cloud Services", 1, 450000, 0, 1),
        ("Microsoft 365 Licenses", "Software", 25, 8500, 0, 20),
        ("Laptop - ThinkPad T14", "Hardware", 3, 650000, 0, 2),
        ("UPS Battery Backup", "Hardware", 5, 85000, 0, 2),
        ("Internet Bandwidth (Gbps)", "Infrastructure", 1, 180000, 0, 1),
    ]
    for name, cat, qty, cost, price, reorder in products:
        inv_table.put_item(Item={
            "org_id": org_id, "item_id": _id("inventory_item"),
            "name": name, "category": cat,
            "quantity_on_hand": dec(qty), "unit": "units",
            "unit_cost": dec(cost), "selling_price": dec(price) if price > 0 else None,
            "reorder_point": dec(reorder),
            "created_at": iso(now), "last_updated": iso(now),
        })

    # Transactions — project-based revenue, monthly recurring
    for day_offset in range(30):
        dt = now - timedelta(days=day_offset)
        # Revenue: larger but less frequent
        if random.random() > 0.5:
            txn_table.put_item(Item={
                "org_id": org_id, "transaction_id": _id("transaction"),
                "business_id": org_id,
                "transaction_type": "revenue",
                "category": random.choice(["Software Development", "IT Consulting", "Support Contract", "Cloud Migration"]),
                "amount": dec(random.uniform(150000, 2500000)),
                "currency": "NGN",
                "counterparty_name": random.choice(["First Bank Nigeria", "GTBank", "Flutterwave", "Paystack", "Interswitch", "Sterling Bank"]),
                "description": random.choice(["Sprint milestone payment", "Monthly retainer", "Project delivery", "Support contract renewal"]),
                "date": iso(dt), "payment_status": random.choice(["paid", "paid", "pending", "partial"]),
                "created_at": iso(dt),
            })
        # Expenses: salaries, cloud, office
        if random.random() > 0.3:
            cat = random.choice(["Staff Salary", "Cloud Infrastructure", "Office Rent", "Internet", "Equipment", "Training"])
            amounts = {
                "Staff Salary": random.uniform(250000, 800000),
                "Cloud Infrastructure": random.uniform(100000, 450000),
                "Office Rent": 350000 if day_offset == 0 else 0,
                "Internet": 180000 if day_offset == 0 else 0,
                "Equipment": random.uniform(50000, 650000),
                "Training": random.uniform(25000, 150000),
            }
            amt = amounts.get(cat, random.uniform(20000, 100000))
            if amt > 0:
                txn_table.put_item(Item={
                    "org_id": org_id, "transaction_id": _id("transaction"),
                    "business_id": org_id,
                    "transaction_type": "expense",
                    "category": cat,
                    "amount": dec(amt),
                    "currency": "NGN",
                    "counterparty_name": random.choice(["AWS Nigeria", "Staff", "MainOne Internet", "Landlord"]),
                    "description": f"{cat} payment",
                    "date": iso(dt), "payment_status": "paid",
                    "created_at": iso(dt),
                })

    alerts_data = [
        ("overdue_payment", "critical", "First Bank: ₦1.8M Invoice Overdue", "Project milestone delivered 30 days ago. Payment terms were net-15.", "Escalate to relationship manager and send formal demand"),
        ("cashflow_warning", "warning", "Salary Week: ₦3.2M Due Friday", "Staff salaries due in 4 days. Current balance is ₦2.1M with ₦1.5M receivables pending.", "Follow up on Flutterwave and Paystack invoices"),
        ("expense_spike", "info", "AWS Costs Up 25% This Month", "Cloud spend increased from ₦360,000 to ₦450,000. New client onboarding drove usage.", "Review resource allocation and consider reserved instances"),
    ]
    for atype, sev, title, desc, action in alerts_data:
        alert_table.put_item(Item={
            "org_id": org_id, "alert_id": _id("alert"),
            "business_id": org_id, "alert_type": atype, "severity": sev,
            "title": title, "description": desc, "recommended_action": action,
            "is_read": False, "created_at": iso(now),
        })


if __name__ == "__main__":
    print("Fetching org IDs from user accounts...")
    starter_org = get_org_id("starter@demo.com")
    growth_org = get_org_id("growth@demo.com")
    business_org = get_org_id("business@demo.com")

    print(f"\nSeeding realistic data...")
    seed_ades_trading(starter_org)
    seed_greenfield_farms(growth_org)
    seed_techbridge(business_org)

    print("\nDone! Data seeded for all test accounts.")
    print("\n--- Test Accounts ---")
    print(f"{'Email':<30} {'Password':<15} {'Role':<15} {'Tier':<12} {'Business'}")
    print("-" * 100)
    print(f"{'admin@smecontroltower.com':<30} {'Admin@2025!':<15} {'super_admin':<15} {'enterprise':<12} SME Control Tower")
    print(f"{'starter@demo.com':<30} {'Demo@2025!':<15} {'owner':<15} {'starter':<12} Ade's Trading Co")
    print(f"{'growth@demo.com':<30} {'Demo@2025!':<15} {'owner':<15} {'growth':<12} GreenField Farms")
    print(f"{'business@demo.com':<30} {'Demo@2025!':<15} {'owner':<15} {'business':<12} TechBridge Solutions")
