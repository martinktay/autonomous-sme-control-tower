import boto3
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.config import get_settings

settings = get_settings()


class DynamoDBService:
    """DynamoDB service for data persistence"""
    
    def __init__(self):
        self.client = boto3.resource(
            "dynamodb",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None
        )
        
        self.signals_table = self.client.Table(settings.signals_table)
        self.nsi_table = self.client.Table(settings.nsi_scores_table)
        self.strategies_table = self.client.Table(settings.strategies_table)
        self.actions_table = self.client.Table(settings.actions_table)
    
    def put_signal(self, signal_data: Dict[str, Any]) -> None:
        """Store signal in DynamoDB"""
        self.signals_table.put_item(Item=signal_data)
    
    def get_signals(self, org_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve signals for an organization"""
        response = self.signals_table.query(
            KeyConditionExpression="org_id = :org_id",
            ExpressionAttributeValues={":org_id": org_id},
            Limit=limit,
            ScanIndexForward=False
        )
        return response.get("Items", [])
    
    def put_nsi_score(self, nsi_data: Dict[str, Any]) -> None:
        """Store NSI score"""
        self.nsi_table.put_item(Item=nsi_data)
    
    def get_latest_nsi(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Get most recent NSI score for organization"""
        response = self.nsi_table.query(
            KeyConditionExpression="org_id = :org_id",
            ExpressionAttributeValues={":org_id": org_id},
            Limit=1,
            ScanIndexForward=False
        )
        items = response.get("Items", [])
        return items[0] if items else None
    
    def put_strategy(self, strategy_data: Dict[str, Any]) -> None:
        """Store strategy simulation"""
        self.strategies_table.put_item(Item=strategy_data)
    
    def put_action(self, action_data: Dict[str, Any]) -> None:
        """Store action execution record"""
        self.actions_table.put_item(Item=action_data)
    
    def get_actions(self, org_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve action history"""
        response = self.actions_table.query(
            KeyConditionExpression="org_id = :org_id",
            ExpressionAttributeValues={":org_id": org_id},
            Limit=limit,
            ScanIndexForward=False
        )
        return response.get("Items", [])


_ddb_service: Optional[DynamoDBService] = None


def get_ddb_service() -> DynamoDBService:
    """Get singleton DynamoDB service"""
    global _ddb_service
    if _ddb_service is None:
        _ddb_service = DynamoDBService()
    return _ddb_service
