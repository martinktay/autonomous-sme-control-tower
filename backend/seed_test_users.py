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
        "business_type": "professional_service",
        "phone": "+2349000000001",
    },
    {
        "email": "starter@demo.com",
        "password": "Demo@2025!",
        "full_name": "Ade Bakare",
        "business_name": "Ade's Trading Co",
        "role": "owner",
        "tier": "starter",
        "business_type": "supermarket",
        "phone": "+2348012345678",
    },
    {
        "email": "growth@demo.com",
        "password": "Demo@2025!",
        "full_name": "Ngozi Okafor",
        "business_name": "GreenField Farms",
        "role": "owner",
        "tier": "growth",
        "business_type": "agriculture",
        "phone": "+2348023456789",
    },
    {
        "email": "business@demo.com",
        "password": "Demo@2025!",
        "full_name": "Chidi Eze",
        "business_name": "TechBridge Solutions",
        "role": "owner",
        "tier": "business",
        "business_type": "professional_service",
        "phone": "+2348034567890",
    },
]


async def main():
    svc = get_auth_service()

    for u in TEST_USERS:
        existing = svc._get_user_by_email(u["email"])
        if existing:
            # Re-hash password + update role, tier, verified
            from app.services.auth_service import _hash_password
            pw_hash, pw_salt = _hash_password(u["password"])
            svc.users_table.update_item(
                Key={"email": u["email"]},
                UpdateExpression="SET #r = :r, tier = :t, email_verified = :v, phone = :p, business_type = :bt, country = :c, pw_hash = :h, pw_salt = :s",
                ExpressionAttributeNames={"#r": "role"},
                ExpressionAttributeValues={
                    ":r": u["role"], ":t": u["tier"], ":v": True,
                    ":p": u.get("phone", ""), ":bt": u.get("business_type", "other"),
                    ":c": u.get("country", "NG"),
                    ":h": pw_hash, ":s": pw_salt,
                },
            )
            print(f"  Updated: {u['email']} -> {u['role']} / {u['tier']}")
        else:
            await svc.register(
                email=u["email"],
                password=u["password"],
                full_name=u["full_name"],
                phone=u.get("phone", ""),
                business_name=u["business_name"],
                business_type=u.get("business_type", "other"),
            )
            svc.users_table.update_item(
                Key={"email": u["email"]},
                UpdateExpression="SET #r = :r, tier = :t, email_verified = :v, country = :c",
                ExpressionAttributeNames={"#r": "role"},
                ExpressionAttributeValues={":r": u["role"], ":t": u["tier"], ":v": True, ":c": u.get("country", "NG")},
            )
            print(f"  Created: {u['email']} -> {u['role']} / {u['tier']}")

    print("\n--- Test Credentials ---")
    print(f"{'Email':<30} {'Password':<15} {'Role':<15} {'Tier'}")
    print("-" * 75)
    for u in TEST_USERS:
        print(f"{u['email']:<30} {u['password']:<15} {u['role']:<15} {u['tier']}")


if __name__ == "__main__":
    asyncio.run(main())
