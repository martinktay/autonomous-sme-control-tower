"""
Seed a super_admin user for testing.

Usage:
  python seed_super_admin.py

Creates a super_admin user with enterprise tier so all features are unlocked.
Credentials are printed to stdout.
"""

import asyncio
import sys
import os

# Add parent to path so app imports work
sys.path.insert(0, os.path.dirname(__file__))

from app.services.auth_service import get_auth_service


ADMIN_EMAIL = "admin@smecontroltower.com"
ADMIN_PASSWORD = "Admin@2025!"
ADMIN_NAME = "Platform Admin"
ADMIN_BUSINESS = "SME Control Tower"


async def main():
    svc = get_auth_service()

    # Check if already exists
    existing = svc._get_user_by_email(ADMIN_EMAIL)
    if existing:
        # Update to super_admin + enterprise if not already
        svc.users_table.update_item(
            Key={"email": ADMIN_EMAIL},
            UpdateExpression="SET #r = :r, tier = :t",
            ExpressionAttributeNames={"#r": "role"},
            ExpressionAttributeValues={":r": "super_admin", ":t": "enterprise"},
        )
        print(f"Updated existing user to super_admin + enterprise tier")
        print(f"  Email:    {ADMIN_EMAIL}")
        print(f"  Password: {ADMIN_PASSWORD}")
        return

    # Register new user
    result = await svc.register(
        email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD,
        full_name=ADMIN_NAME,
        business_name=ADMIN_BUSINESS,
    )

    # Upgrade to super_admin + enterprise
    svc.users_table.update_item(
        Key={"email": ADMIN_EMAIL},
        UpdateExpression="SET #r = :r, tier = :t",
        ExpressionAttributeNames={"#r": "role"},
        ExpressionAttributeValues={":r": "super_admin", ":t": "enterprise"},
    )

    print("Super admin created successfully!")
    print(f"  Email:    {ADMIN_EMAIL}")
    print(f"  Password: {ADMIN_PASSWORD}")
    print(f"  Org ID:   {result['org_id']}")
    print(f"  Role:     super_admin")
    print(f"  Tier:     enterprise")


if __name__ == "__main__":
    asyncio.run(main())
