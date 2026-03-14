"""Clear all demo data from DynamoDB tables for a fresh demo start."""
import sys
import os
import boto3
sys.path.insert(0, os.path.dirname(__file__))

from app.config import get_settings

settings = get_settings()

session = boto3.Session(
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region,
)
ddb = session.resource("dynamodb")

TABLES = [
    settings.signals_table,
    settings.nsi_scores_table,
    settings.strategies_table,
    settings.actions_table,
    settings.evaluations_table,
    settings.embeddings_table,
    settings.tasks_table,
]

DEMO_ORGS = [
    "demo-org-001",
    "demo-org-002",
    "demo-org-003",
    "demo-org-004",
    "demo-org-005",
]


def clear_table(table_name: str):
    """Scan for demo org items and delete them."""
    try:
        table = ddb.Table(table_name)
        key_schema = table.key_schema
        key_names = [k["AttributeName"] for k in key_schema]
        deleted = 0

        for org_id in DEMO_ORGS:
            response = table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key("org_id").eq(org_id),
            )
            items = response.get("Items", [])
            while response.get("LastEvaluatedKey"):
                response = table.query(
                    KeyConditionExpression=boto3.dynamodb.conditions.Key("org_id").eq(org_id),
                    ExclusiveStartKey=response["LastEvaluatedKey"],
                )
                items.extend(response.get("Items", []))

            with table.batch_writer() as batch:
                for item in items:
                    key = {k: item[k] for k in key_names if k in item}
                    batch.delete_item(Key=key)
                    deleted += 1

        print(f"  {table_name}: deleted {deleted} items")
    except Exception as e:
        print(f"  {table_name}: skipped ({e})")


if __name__ == "__main__":
    print("Clearing demo data from DynamoDB...")
    for t in TABLES:
        clear_table(t)
    print("\nDone! All demo org data cleared.")
