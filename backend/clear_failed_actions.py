"""Delete all failed actions from DynamoDB for demo orgs."""
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

ddb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
table = ddb.Table("autonomous-sme-actions")

orgs = ["demo-org-001", "demo-org-002", "demo-org-003", "demo-org-004", "demo-org-005"]
deleted = 0

for org in orgs:
    resp = table.query(
        KeyConditionExpression="org_id = :o",
        ExpressionAttributeValues={":o": org},
    )
    for item in resp.get("Items", []):
        if item.get("execution_status") == "failed":
            table.delete_item(Key={"org_id": item["org_id"], "action_id": item["action_id"]})
            deleted += 1
            print(f"Deleted failed action for {org}")

print(f"Done. Deleted {deleted} failed actions total.")
