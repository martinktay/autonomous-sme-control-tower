"""Upload all 5 demo CSV files to the backend finance endpoint."""
import requests
import os

BASE = "http://localhost:8000"

UPLOADS = [
    ("demo-org-001", "ades_trading_co.csv"),
    ("demo-org-002", "greenfield_farms.csv"),
    ("demo-org-003", "techbridge_solutions.csv"),
    ("demo-org-004", "brighton_craft_bakery.csv"),
    ("demo-org-005", "thames_valley_plumbing.csv"),
]

script_dir = os.path.dirname(os.path.abspath(__file__))

for org_id, filename in UPLOADS:
    filepath = os.path.join(script_dir, filename)
    with open(filepath, "rb") as f:
        resp = requests.post(
            f"{BASE}/api/finance/upload",
            params={"org_id": org_id},
            files={"file": (filename, f, "text/csv")},
            timeout=30,
        )
    if resp.ok:
        data = resp.json()
        print(f"OK  {org_id} ({filename}): {data.get('records_imported', '?')} records imported")
    else:
        print(f"ERR {org_id} ({filename}): {resp.status_code} - {resp.text[:200]}")

print("\nDone! All demo data uploaded.")
