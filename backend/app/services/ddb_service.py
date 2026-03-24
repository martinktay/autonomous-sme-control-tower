"""
DynamoDB persistence service — all table operations for the SME Control Tower.

Provides CRUD + query methods for signals, NSI scores, strategies, actions,
evaluations, and generic table access. Every write enforces org_id presence
and format. Reads/writes use exponential-backoff retry for throttling resilience.
Float ↔ Decimal and datetime ↔ ISO-string conversions are handled transparently.
"""

import boto3
import time
import logging
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal
from botocore.exceptions import ClientError
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class DynamoDBService:
    """DynamoDB service for data persistence with error handling and retry logic"""
    
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
        self.evaluations_table = self.client.Table(settings.evaluations_table)
        self.embeddings_table = self.client.Table(settings.embeddings_table)
    
    def _retry_with_backoff(self, func, *args, max_retries: int = 3, **kwargs):
        """Retry logic with exponential backoff for DynamoDB operations"""
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "")
                error_message = e.response.get("Error", {}).get("Message", "")
                
                logger.error(
                    f"DynamoDB ClientError on attempt {attempt + 1}/{max_retries}: "
                    f"Code={error_code}, Message={error_message}"
                )
                
                # Don't retry on validation errors
                if error_code in ["ValidationException", "ResourceNotFoundException"]:
                    raise e
                
                # Retry on throttling and service errors
                if error_code in ["ProvisionedThroughputExceededException", "ThrottlingException", "ServiceUnavailable"]:
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + (time.time() % 1)  # Exponential backoff with jitter
                        logger.info(f"Retrying after {wait_time:.2f} seconds...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Max retries reached for {error_code}")
                        raise e
                else:
                    raise e
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}/{max_retries}: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + (time.time() % 1)
                    time.sleep(wait_time)
                else:
                    raise e
    
    def _convert_to_dynamodb_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Python types to DynamoDB-compatible types"""
        converted = {}
        for key, value in data.items():
            if isinstance(value, float):
                converted[key] = Decimal(str(value))
            elif isinstance(value, datetime):
                converted[key] = value.isoformat()
            elif isinstance(value, dict):
                converted[key] = self._convert_to_dynamodb_format(value)
            elif isinstance(value, list):
                converted[key] = [
                    self._convert_to_dynamodb_format(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                converted[key] = value
        return converted
    
    def _convert_from_dynamodb_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert DynamoDB types to Python types"""
        converted = {}
        for key, value in data.items():
            if isinstance(value, Decimal):
                converted[key] = float(value)
            elif isinstance(value, dict):
                converted[key] = self._convert_from_dynamodb_format(value)
            elif isinstance(value, list):
                converted[key] = [
                    self._convert_from_dynamodb_format(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                converted[key] = value
        return converted
    
    def _enforce_org_id(self, data: Dict[str, Any], org_id: str) -> None:
        """Enforce org_id is present and well-formed in data"""
        import re
        if "org_id" not in data:
            raise ValueError("org_id is required for all DynamoDB operations")
        if data["org_id"] != org_id:
            raise ValueError(f"org_id mismatch: expected {org_id}, got {data['org_id']}")
        if not re.match(r"^org-[a-z0-9]{12}$", org_id):
            raise ValueError(f"Invalid org_id format: {org_id}")
    
    # ==================== CREATE OPERATIONS ====================
    
    def create_signal(self, signal_data: Dict[str, Any]) -> None:
        """Create a new signal record"""
        self._enforce_org_id(signal_data, signal_data.get("org_id", ""))
        converted_data = self._convert_to_dynamodb_format(signal_data)
        logger.info(f"Creating signal {signal_data.get('signal_id')} for org {signal_data.get('org_id')}")
        self._retry_with_backoff(self.signals_table.put_item, Item=converted_data)
    
    def create_nsi_score(self, nsi_data: Dict[str, Any]) -> None:
        """Create a new NSI score record"""
        self._enforce_org_id(nsi_data, nsi_data.get("org_id", ""))
        # DynamoDB table uses timestamp as sort key — ensure it's present
        if "timestamp" not in nsi_data:
            from datetime import datetime, timezone
            nsi_data["timestamp"] = datetime.now(timezone.utc).isoformat()
        converted_data = self._convert_to_dynamodb_format(nsi_data)
        logger.info(f"Creating NSI score {nsi_data.get('nsi_id')} for org {nsi_data.get('org_id')}")
        self._retry_with_backoff(self.nsi_table.put_item, Item=converted_data)
    
    def create_strategy(self, strategy_data: Dict[str, Any]) -> None:
        """Create a new strategy record"""
        self._enforce_org_id(strategy_data, strategy_data.get("org_id", ""))
        # DynamoDB table uses simulation_id as sort key — map from strategy_id
        if "simulation_id" not in strategy_data and "strategy_id" in strategy_data:
            strategy_data["simulation_id"] = strategy_data["strategy_id"]
        converted_data = self._convert_to_dynamodb_format(strategy_data)
        logger.info(f"Creating strategy {strategy_data.get('strategy_id')} for org {strategy_data.get('org_id')}")
        self._retry_with_backoff(self.strategies_table.put_item, Item=converted_data)
    
    def create_action(self, action_data: Dict[str, Any]) -> None:
        """Create a new action execution record"""
        self._enforce_org_id(action_data, action_data.get("org_id", ""))
        # DynamoDB table uses action_id as sort key — map from execution_id
        if "action_id" not in action_data and "execution_id" in action_data:
            action_data["action_id"] = action_data["execution_id"]
        converted_data = self._convert_to_dynamodb_format(action_data)
        logger.info(f"Creating action {action_data.get('execution_id')} for org {action_data.get('org_id')}")
        self._retry_with_backoff(self.actions_table.put_item, Item=converted_data)
    
    def create_evaluation(self, evaluation_data: Dict[str, Any]) -> None:
        """Create a new evaluation record"""
        self._enforce_org_id(evaluation_data, evaluation_data.get("org_id", ""))
        converted_data = self._convert_to_dynamodb_format(evaluation_data)
        logger.info(f"Creating evaluation {evaluation_data.get('evaluation_id')} for org {evaluation_data.get('org_id')}")
        self._retry_with_backoff(self.evaluations_table.put_item, Item=converted_data)
    
    # ==================== READ OPERATIONS ====================
    
    def get_signal(self, org_id: str, signal_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific signal by org_id and signal_id"""
        def _get():
            response = self.signals_table.get_item(
                Key={"org_id": org_id, "signal_id": signal_id}
            )
            item = response.get("Item")
            return self._convert_from_dynamodb_format(item) if item else None
        
        logger.info(f"Getting signal {signal_id} for org {org_id}")
        return self._retry_with_backoff(_get)
    
    def get_nsi_score(self, org_id: str, nsi_id: str, timestamp: str = None) -> Optional[Dict[str, Any]]:
        """Get a specific NSI score by org_id and timestamp (sort key)"""
        if timestamp:
            def _get():
                response = self.nsi_table.get_item(
                    Key={"org_id": org_id, "timestamp": timestamp}
                )
                item = response.get("Item")
                return self._convert_from_dynamodb_format(item) if item else None
            logger.info(f"Getting NSI score for org {org_id} at {timestamp}")
            return self._retry_with_backoff(_get)
        else:
            # Fallback: query and filter by nsi_id
            scores = self.query_nsi_scores(org_id, limit=100)
            for score in scores:
                if score.get("nsi_id") == nsi_id:
                    return score
            return None
    
    def get_strategy(self, org_id: str, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific strategy by org_id and strategy_id"""
        def _get():
            response = self.strategies_table.get_item(
                Key={"org_id": org_id, "simulation_id": strategy_id}
            )
            item = response.get("Item")
            return self._convert_from_dynamodb_format(item) if item else None
        
        logger.info(f"Getting strategy {strategy_id} for org {org_id}")
        return self._retry_with_backoff(_get)
    
    def get_action(self, org_id: str, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific action by org_id and execution_id"""
        def _get():
            response = self.actions_table.get_item(
                Key={"org_id": org_id, "action_id": execution_id}
            )
            item = response.get("Item")
            return self._convert_from_dynamodb_format(item) if item else None
        
        logger.info(f"Getting action {execution_id} for org {org_id}")
        return self._retry_with_backoff(_get)
    
    def get_evaluation(self, org_id: str, evaluation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific evaluation by org_id and evaluation_id"""
        def _get():
            response = self.evaluations_table.get_item(
                Key={"org_id": org_id, "evaluation_id": evaluation_id}
            )
            item = response.get("Item")
            return self._convert_from_dynamodb_format(item) if item else None
        
        logger.info(f"Getting evaluation {evaluation_id} for org {org_id}")
        return self._retry_with_backoff(_get)
    
    # ==================== QUERY OPERATIONS (filtered by org_id) ====================
    
    def query_signals(self, org_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Query signals for an organization"""
        def _query():
            response = self.signals_table.query(
                KeyConditionExpression="org_id = :org_id",
                ExpressionAttributeValues={":org_id": org_id},
                Limit=limit,
                ScanIndexForward=False
            )
            items = response.get("Items", [])
            return [self._convert_from_dynamodb_format(item) for item in items]
        
        logger.info(f"Querying signals for org {org_id} (limit={limit})")
        return self._retry_with_backoff(_query)
    
    def query_nsi_scores(self, org_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Query NSI scores for an organization"""
        def _query():
            response = self.nsi_table.query(
                KeyConditionExpression="org_id = :org_id",
                ExpressionAttributeValues={":org_id": org_id},
                Limit=limit,
                ScanIndexForward=False
            )
            items = response.get("Items", [])
            return [self._convert_from_dynamodb_format(item) for item in items]
        
        logger.info(f"Querying NSI scores for org {org_id} (limit={limit})")
        return self._retry_with_backoff(_query)
    
    def query_strategies(self, org_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Query strategies for an organization"""
        def _query():
            response = self.strategies_table.query(
                KeyConditionExpression="org_id = :org_id",
                ExpressionAttributeValues={":org_id": org_id},
                Limit=limit,
                ScanIndexForward=False
            )
            items = response.get("Items", [])
            return [self._convert_from_dynamodb_format(item) for item in items]
        
        logger.info(f"Querying strategies for org {org_id} (limit={limit})")
        return self._retry_with_backoff(_query)
    
    def query_actions(self, org_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Query action executions for an organization"""
        def _query():
            response = self.actions_table.query(
                KeyConditionExpression="org_id = :org_id",
                ExpressionAttributeValues={":org_id": org_id},
                Limit=limit,
                ScanIndexForward=False
            )
            items = response.get("Items", [])
            return [self._convert_from_dynamodb_format(item) for item in items]
        
        logger.info(f"Querying actions for org {org_id} (limit={limit})")
        return self._retry_with_backoff(_query)
    
    def query_evaluations(self, org_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Query evaluations for an organization"""
        def _query():
            response = self.evaluations_table.query(
                KeyConditionExpression="org_id = :org_id",
                ExpressionAttributeValues={":org_id": org_id},
                Limit=limit,
                ScanIndexForward=False
            )
            items = response.get("Items", [])
            return [self._convert_from_dynamodb_format(item) for item in items]
        
        logger.info(f"Querying evaluations for org {org_id} (limit={limit})")
        return self._retry_with_backoff(_query)
    
    def get_latest_nsi(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Get most recent NSI score for organization"""
        def _query():
            response = self.nsi_table.query(
                KeyConditionExpression="org_id = :org_id",
                ExpressionAttributeValues={":org_id": org_id},
                Limit=1,
                ScanIndexForward=False
            )
            items = response.get("Items", [])
            if items:
                return self._convert_from_dynamodb_format(items[0])
            return None
        
        logger.info(f"Getting latest NSI for org {org_id}")
        return self._retry_with_backoff(_query)
    
    # ==================== UPDATE OPERATIONS ====================
    
    def update_signal(self, org_id: str, signal_id: str, updates: Dict[str, Any]) -> None:
        """Update a signal record"""
        self._enforce_org_id({"org_id": org_id}, org_id)
        converted_updates = self._convert_to_dynamodb_format(updates)
        
        # Build update expression
        update_expr_parts = []
        expr_attr_values = {}
        expr_attr_names = {}
        
        for key, value in converted_updates.items():
            if key not in ["org_id", "signal_id"]:  # Don't update keys
                placeholder = f"#{key}"
                value_placeholder = f":{key}"
                update_expr_parts.append(f"{placeholder} = {value_placeholder}")
                expr_attr_names[placeholder] = key
                expr_attr_values[value_placeholder] = value
        
        if not update_expr_parts:
            logger.warning(f"No valid fields to update for signal {signal_id}")
            return
        
        update_expression = "SET " + ", ".join(update_expr_parts)
        
        def _update():
            self.signals_table.update_item(
                Key={"org_id": org_id, "signal_id": signal_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expr_attr_names,
                ExpressionAttributeValues=expr_attr_values
            )
        
        logger.info(f"Updating signal {signal_id} for org {org_id}")
        self._retry_with_backoff(_update)
    
    def update_action(self, org_id: str, execution_id: str, updates: Dict[str, Any]) -> None:
        """Update an action execution record"""
        self._enforce_org_id({"org_id": org_id}, org_id)
        converted_updates = self._convert_to_dynamodb_format(updates)
        
        # Build update expression
        update_expr_parts = []
        expr_attr_values = {}
        expr_attr_names = {}
        
        for key, value in converted_updates.items():
            if key not in ["org_id", "action_id", "execution_id"]:  # Don't update keys
                placeholder = f"#{key}"
                value_placeholder = f":{key}"
                update_expr_parts.append(f"{placeholder} = {value_placeholder}")
                expr_attr_names[placeholder] = key
                expr_attr_values[value_placeholder] = value
        
        if not update_expr_parts:
            logger.warning(f"No valid fields to update for action {execution_id}")
            return
        
        update_expression = "SET " + ", ".join(update_expr_parts)
        
        def _update():
            self.actions_table.update_item(
                Key={"org_id": org_id, "action_id": execution_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expr_attr_names,
                ExpressionAttributeValues=expr_attr_values
            )
        
        logger.info(f"Updating action {execution_id} for org {org_id}")
        self._retry_with_backoff(_update)
    
    # ==================== LEGACY COMPATIBILITY METHODS ====================
    
    def put_signal(self, signal_data: Dict[str, Any]) -> None:
        """Legacy method - use create_signal instead"""
        self.create_signal(signal_data)
    
    def get_signals(self, org_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Legacy method - use query_signals instead"""
        return self.query_signals(org_id, limit)
    
    def put_nsi_score(self, nsi_data: Dict[str, Any]) -> None:
        """Legacy method - use create_nsi_score instead"""
        self.create_nsi_score(nsi_data)
    
    def put_strategy(self, strategy_data: Dict[str, Any]) -> None:
        """Legacy method - use create_strategy instead"""
        self.create_strategy(strategy_data)
    
    def put_action(self, action_data: Dict[str, Any]) -> None:
        """Legacy method - use create_action instead"""
        self.create_action(action_data)
    
    def get_actions(self, org_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Legacy method - use query_actions instead"""
        return self.query_actions(org_id, limit)



    # ==================== GENERIC OPERATIONS (for memory service) ====================

    def put_item(self, table_name: str, item: Dict[str, Any]) -> None:
        """Put an item into any table by name. Logs warning if table doesn't exist."""
        table = self.client.Table(table_name)
        converted = self._convert_to_dynamodb_format(item)
        try:
            self._retry_with_backoff(table.put_item, Item=converted)
        except Exception as e:
            if "ResourceNotFoundException" in str(type(e).__name__) or "ResourceNotFoundException" in str(e):
                logger.warning("Table %s not found, skipping put_item", table_name)
                return
            raise

    def get_item(self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get an item from any table by name and key. Returns None if table doesn't exist."""
        table = self.client.Table(table_name)
        def _get():
            response = table.get_item(Key=key)
            item = response.get("Item")
            return self._convert_from_dynamodb_format(item) if item else None
        try:
            return self._retry_with_backoff(_get)
        except Exception as e:
            if "ResourceNotFoundException" in str(type(e).__name__) or "ResourceNotFoundException" in str(e):
                logger.warning("Table %s not found, returning None", table_name)
                return None
            raise

    def query_items(
        self,
        table_name: str,
        key_condition: str,
        expression_values: Dict[str, Any],
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Query items from any table by name. Returns empty list if table doesn't exist."""
        table = self.client.Table(table_name)
        def _query():
            response = table.query(
                KeyConditionExpression=key_condition,
                ExpressionAttributeValues=expression_values,
                Limit=limit,
            )
            items = response.get("Items", [])
            return [self._convert_from_dynamodb_format(item) for item in items]
        try:
            return self._retry_with_backoff(_query)
        except Exception as e:
            if "ResourceNotFoundException" in str(type(e).__name__) or "ResourceNotFoundException" in str(e):
                logger.warning("Table %s not found, returning empty list", table_name)
                return []
            raise


_ddb_service: Optional[DynamoDBService] = None
_ddb_lock = threading.Lock()


def get_ddb_service() -> DynamoDBService:
    """Get singleton DynamoDB service (thread-safe)"""
    global _ddb_service
    if _ddb_service is None:
        with _ddb_lock:
            if _ddb_service is None:
                _ddb_service = DynamoDBService()
    return _ddb_service
