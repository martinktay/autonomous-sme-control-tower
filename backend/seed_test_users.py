"""
Seed test users for development and demo.

Usage:
  python seed_test_users.py

Creates:
  1. Super Admin (enterprise tier, all features unlocked)
  2. SME Owner - Starter tier (free)
  3. SME Owner - Growth tier
  4. SME Owner - Business tier
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.services.auth_service import get_auth_service

TEST_USERS = [
    {
        "email": "admin@smecontroltower.com",
        "password": "Admin@2025!",
        "full_name": "Platform Admin",
        "business_name": "SME Control Tower",
        "role": "super_admin",
        "tier": "enterprise",
    },
    {
        "email": "starter@demo.com",
        "password": "Demo@2025!",
        "full_name": "Ade Bakare",
        "business_name": "Ade's Trading Co",
        "role": "owner",
        "tier": "starter",
    },
    {
        "email": "growth@demo.com",
        "password": "Demo@2025!",
        "full_name": "Ngozi Okafor",
        "business_name": "GreenField Farms",
        "role": "owner",
        "tier": "growth",
    },
    {
        "email": "business@demo.com",
        "password": "Demo@2025!",
        "full_name": "Chidi Eze",
        "business_name": "TechBridge Solutions",
        "role": "owner",
        "tier": "business",
    },
]


async def main():
    svc = get_auth_service()

    for u in TEST_USERS:
        existing = svc._get_user_by_email(u["email"])
        if existing:
            # Update role and tier
            svc.users_table.update_item(
                Key={"email": u["email"]},
                UpdateExpression="SET #r = :r, tier = :t",
                ExpressionAttributeNames={"#r": "role"},
                ExpressionAttributeValues={":r": u["role"], ":t": u["tier"]},
            )
            print(f"  Updated: {u['email']} -> {u['role']} / {u['tier']}")
        else:
            await svc.register(
                email=u["email"],
                password=u["password"],
                full_name=u["full_name"],
                business_name=u["business_name"],
            )
            svc.users_table.update_item(
                Key={"email": u["email"]},
                UpdateExpression="SET #r = :r, tier = :t",
                ExpressionAttributeNames={"#r": "role"},
                ExpressionAttributeValues={":r": u["role"], ":t": u["tier"]},
            )
            print(f"  Created: {u['email']} -> {u['role']} / {u['tier']}")

    print("\n--- Test Credentials ---")
    print(f"{'Email':<30} {'Password':<15} {'Role':<15} {'Tier'}")
    print("-" * 75)
    for u in TEST_USERS:
        print(f"{u['email']:<30} {u['password']:<15} {u['role']:<15} {u['tier']}")


if __name__ == "__main__":
    asyncio.run(main())
