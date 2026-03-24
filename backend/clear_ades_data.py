"""Clear all DynamoDB data for Ades Trading Co (demo-org-001) only."""
import sys, os
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

ORG_ID = "demo-org-001"

TABLES = [
    settings.signals_table,
    settings.bsi_scores_table,
    settings.strategies_table,
    settings.actions_table,
    settings.evaluations_table,
    settings.embeddings_table,
    settings.tasks_table,
]

def clear_table(table_name: str):
    try:
        table = ddb.Table(table_name)
        key_names = [k["AttributeName"] for k in table.key_schema]
        resp = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("org_id").eq(ORG_ID),
        )
        items = resp.get("Items", [])
        while resp.get("LastEvaluatedKey"):
            resp = table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key("org_id").eq(ORG_ID),
                ExclusiveStartKey=resp["LastEvaluatedKey"],
            )
            items.extend(resp.get("Items", []))
        with table.batch_writer() as batch:
            for item in items:
                batch.delete_item(Key={k: item[k] for k in key_names if k in item})
        print(f"  {table_name}: deleted {len(items)} items")
    except Exception as e:
        print(f"  {table_name}: skipped ({e})")

if __name__ == "__main__":
    print(f"Clearing all data for {ORG_ID} (Ades Trading Co)...")
    for t in TABLES:
        clear_table(t)
    print("\nDone! Ades Trading Co data cleared.")
