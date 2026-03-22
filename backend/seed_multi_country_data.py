"""
Seed multi-country demo accounts for testing country-aware features.

Usage:
  python seed_multi_country_data.py

Creates accounts for GH, KE, ZA, RW, GB with realistic business names,
transactions, and login credentials.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.services.auth_service import get_auth_service
from app.services.transaction_service import get_transaction_service
from app.utils.id_generator import generate_id

MULTI_COUNTRY_USERS = [
    {
        "email": "ghana@demo.com",
        "password": "Demo@2025!",
        "full_name": "Kwame Asante",
        "business_name": "Asante Fresh Market",
        "role": "owner",
        "tier": "growth",
        "business_type": "supermarket",
        "phone": "+233241234567",
        "country": "GH",
    },
    {
        "email": "kenya@demo.com",
        "password": "Demo@2025!",
        "full_name": "Wanjiku Mwangi",
        "business_name": "Mwangi Auto Garage",
        "role": "owner",
        "tier": "business",
        "business_type": "auto_mechanic",
        "phone": "+254712345678",
        "country": "KE",
    },
    {
        "email": "southafrica@demo.com",
        "password": "Demo@2025!",
        "full_name": "Thabo Ndlovu",
        "business_name": "Ndlovu Fashion House",
        "role": "owner",
        "tier": "growth",
        "business_type": "fashion_textile",
        "phone": "+27821234567",
        "country": "ZA",
    },
    {
        "email": "rwanda@demo.com",
        "password": "Demo@2025!",
        "full_name": "Uwimana Diane",
        "business_name": "Kigali Pharmacy Plus",
        "role": "owner",
        "tier": "starter",
        "business_type": "pharmacy",
        "phone": "+250781234567",
        "country": "RW",
    },
    {
        "email": "uk@demo.com",
        "password": "Demo@2025!",
        "full_name": "James Okonkwo",
        "business_name": "Thames Valley Plumbing",
        "role": "owner",
        "tier": "business",
        "business_type": "construction",
        "phone": "+447911234567",
        "country": "GB",
    },
]

# Sample transactions per country (revenue + expenses)
SAMPLE_TRANSACTIONS = {
    "GH": [
        {"description": "Daily market sales", "amount": 4500, "transaction_type": "revenue", "category": "sales"},
        {"description": "Wholesale produce purchase", "amount": 2800, "transaction_type": "expense", "category": "inventory"},
        {"description": "Weekend sales", "amount": 6200, "transaction_type": "revenue", "category": "sales"},
        {"description": "Staff wages", "amount": 1500, "transaction_type": "expense", "category": "payroll"},
        {"description": "Delivery service", "amount": 350, "transaction_type": "expense", "category": "logistics"},
    ],
    "KE": [
        {"description": "Vehicle repair service", "amount": 25000, "transaction_type": "revenue", "category": "services"},
        {"description": "Spare parts purchase", "amount": 15000, "transaction_type": "expense", "category": "inventory"},
        {"description": "Engine overhaul", "amount": 45000, "transaction_type": "revenue", "category": "services"},
        {"description": "Workshop rent", "amount": 8000, "transaction_type": "expense", "category": "rent"},
        {"description": "Mechanic wages", "amount": 12000, "transaction_type": "expense", "category": "payroll"},
    ],
    "ZA": [
        {"description": "Clothing sales", "amount": 18500, "transaction_type": "revenue", "category": "sales"},
        {"description": "Fabric purchase", "amount": 8000, "transaction_type": "expense", "category": "inventory"},
        {"description": "Online orders", "amount": 12000, "transaction_type": "revenue", "category": "sales"},
        {"description": "Tailor wages", "amount": 6500, "transaction_type": "expense", "category": "payroll"},
        {"description": "Shop rent", "amount": 4500, "transaction_type": "expense", "category": "rent"},
    ],
    "RW": [
        {"description": "Prescription sales", "amount": 85000, "transaction_type": "revenue", "category": "sales"},
        {"description": "Medicine stock", "amount": 55000, "transaction_type": "expense", "category": "inventory"},
        {"description": "OTC sales", "amount": 35000, "transaction_type": "revenue", "category": "sales"},
        {"description": "Pharmacist salary", "amount": 25000, "transaction_type": "expense", "category": "payroll"},
        {"description": "Utilities", "amount": 5000, "transaction_type": "expense", "category": "utilities"},
    ],
    "GB": [
        {"description": "Plumbing job - residential", "amount": 850, "transaction_type": "revenue", "category": "services"},
        {"description": "Materials purchase", "amount": 320, "transaction_type": "expense", "category": "inventory"},
        {"description": "Emergency callout", "amount": 1200, "transaction_type": "revenue", "category": "services"},
        {"description": "Van fuel", "amount": 180, "transaction_type": "expense", "category": "transport"},
        {"description": "Insurance", "amount": 250, "transaction_type": "expense", "category": "insurance"},
    ],
}


async def main():
    svc = get_auth_service()
    txn_svc = get_transaction_service()

    for u in MULTI_COUNTRY_USERS:
        existing = svc._get_user_by_email(u["email"])
        if existing:
            svc.users_table.update_item(
                Key={"email": u["email"]},
                UpdateExpression="SET #r = :r, tier = :t, email_verified = :v, phone = :p, business_type = :bt, country = :c",
                ExpressionAttributeNames={"#r": "role"},
                ExpressionAttributeValues={
                    ":r": u["role"], ":t": u["tier"], ":v": True,
                    ":p": u.get("phone", ""), ":bt": u.get("business_type", "other"),
                    ":c": u.get("country", "NG"),
                },
            )
            org_id = existing.get("org_id", "")
            print(f"  Updated: {u['email']} -> {u['role']} / {u['tier']} / {u['country']}")
        else:
            result = await svc.register(
                email=u["email"],
                password=u["password"],
                full_name=u["full_name"],
                phone=u.get("phone", ""),
                business_name=u["business_name"],
                business_type=u.get("business_type", "other"),
            )
            org_id = result.get("org_id", "")
            svc.users_table.update_item(
                Key={"email": u["email"]},
                UpdateExpression="SET #r = :r, tier = :t, email_verified = :v, country = :c",
                ExpressionAttributeNames={"#r": "role"},
                ExpressionAttributeValues={
                    ":r": u["role"], ":t": u["tier"], ":v": True,
                    ":c": u.get("country", "NG"),
                },
            )
            print(f"  Created: {u['email']} -> {u['role']} / {u['tier']} / {u['country']}")

        # Seed sample transactions
        country = u.get("country", "NG")
        txns = SAMPLE_TRANSACTIONS.get(country, [])
        if org_id and txns:
            for txn in txns:
                try:
                    txn_svc.create_transaction(org_id, {
                        **txn,
                        "date": "2025-06-15",
                        "currency": {"GH": "GHS", "KE": "KES", "ZA": "ZAR", "RW": "RWF", "GB": "GBP"}.get(country, "NGN"),
                    })
                except Exception:
                    pass  # skip if already exists or table issue
            print(f"    Seeded {len(txns)} transactions for {u['business_name']}")

    print("\n--- Multi-Country Test Credentials ---")
    print(f"{'Email':<25} {'Password':<15} {'Country':<5} {'Tier':<12} {'Business'}")
    print("-" * 90)
    for u in MULTI_COUNTRY_USERS:
        print(f"{u['email']:<25} {u['password']:<15} {u['country']:<5} {u['tier']:<12} {u['business_name']}")


if __name__ == "__main__":
    asyncio.run(main())
