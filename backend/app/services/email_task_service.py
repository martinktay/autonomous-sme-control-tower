"""
Email & Task Service — Manages the full email ingestion pipeline and task lifecycle.

Pipeline: receive email → AI classify → extract tasks → store signal → create task records.
Also supports manual task creation, status updates, and AI-generated reply drafts.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.agents.email_agent import EmailAgent
from app.services.ddb_service import DynamoDBService, get_ddb_service
from app.config import get_settings
from app.utils.id_generator import generate_id

logger = logging.getLogger(__name__)


class EmailTaskService:
    """Orchestrates email classification, task extraction, and task CRUD against DynamoDB."""

    def __init__(self, ddb_service: DynamoDBService):
        self.ddb = ddb_service
        self.agent = EmailAgent()
        self.tasks_table = get_settings().tasks_table

    # ==================== Email Ingestion ====================

    def ingest_email(self, org_id: str, subject: str, body: str, sender: str) -> Dict[str, Any]:
        """Full ingestion pipeline: classify → extract tasks → store signal → create task records.

        Args:
            org_id: Organisation identifier for multi-tenant isolation.
            subject: Email subject line.
            body: Email body text.
            sender: Sender email address.

        Returns:
            Dict with signal_id, classification result, and created tasks.
        """
        signal_id = generate_id("signal")

        # 1. Classify email (category, priority, sentiment) via AI
        try:
            classification = self.agent.classify_email(subject, body, sender)
        except Exception as e:
            logger.error(f"Email classification failed: {e}")
            classification = {
                "category": "other", "priority": "medium",
                "action_required": False, "summary": subject,
                "sentiment": "neutral", "entities": {},
            }

        # 2. Extract actionable tasks from email body via AI
        tasks_data = []
        try:
            extraction = self.agent.extract_tasks(subject, body, sender)
            tasks_data = extraction.get("tasks", [])
        except Exception as e:
            logger.error(f"Task extraction failed: {e}")
            extraction = {"tasks": [], "email_summary": subject}

        # 3. Persist email as a signal in DynamoDB
        signal = {
            "signal_id": signal_id,
            "org_id": org_id,
            "signal_type": "email",
            "content": {
                "subject": subject,
                "body": body,
                "sender": sender,
                "classification": classification,
                "task_extraction": extraction,
            },
            "processing_status": "processed",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.ddb.create_signal(signal)

        # 4. Create individual task records from extracted data
        created_tasks = []
        for t in tasks_data:
            task_record = self._create_task_from_extraction(org_id, t, signal_id)
            created_tasks.append(task_record)

        return {
            "signal_id": signal_id,
            "classification": classification,
            "tasks_created": len(created_tasks),
            "tasks": created_tasks,
        }

    def _create_task_from_extraction(
        self, org_id: str, task_data: Dict[str, Any], source_id: str
    ) -> Dict[str, Any]:
        """Build and persist a task record from AI-extracted task data."""
        task_id = generate_id("task")
        now = datetime.now(timezone.utc).isoformat()

        record = {
            "org_id": org_id,
            "task_id": task_id,
            "title": task_data.get("title", "Untitled task"),
            "description": task_data.get("description", ""),
            "task_type": task_data.get("task_type", "other"),
            "priority": task_data.get("priority", "medium"),
            "status": "pending",
            "source_type": "email",
            "source_id": source_id,
            "due_date": task_data.get("due_hint"),
            "related_entities": task_data.get("related_entities", {}),
            "created_at": now,
            "updated_at": now,
        }
        self.ddb.put_item(self.tasks_table, record)
        return record

    # ==================== Task Management ====================

    def get_tasks(
        self, org_id: str, status: Optional[str] = None, priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get tasks for an org, optionally filtered by status/priority."""
        items = self.ddb.query_items(
            self.tasks_table,
            key_condition="org_id = :org_id",
            expression_values={":org_id": org_id},
            limit=100,
        )
        if status:
            items = [i for i in items if i.get("status") == status]
        if priority:
            items = [i for i in items if i.get("priority") == priority]
        return items

    def get_task(self, org_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a single task by ID."""
        return self.ddb.get_item(
            self.tasks_table,
            {"org_id": org_id, "task_id": task_id},
        )

    def update_task_status(
        self, org_id: str, task_id: str, status: str, result: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update task status (pending → in_progress → completed/cancelled)."""
        task = self.get_task(org_id, task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found for org {org_id}")

        task["status"] = status
        task["updated_at"] = datetime.now(timezone.utc).isoformat()
        if result:
            task["result"] = result

        self.ddb.put_item(self.tasks_table, task)
        return task

    def create_manual_task(self, org_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task manually (not from email)."""
        task_id = generate_id("task")
        now = datetime.now(timezone.utc).isoformat()

        record = {
            "org_id": org_id,
            "task_id": task_id,
            "title": data.get("title", "Untitled"),
            "description": data.get("description", ""),
            "task_type": data.get("task_type", "other"),
            "priority": data.get("priority", "medium"),
            "status": "pending",
            "source_type": "manual",
            "due_date": data.get("due_date"),
            "assigned_to": data.get("assigned_to"),
            "created_at": now,
            "updated_at": now,
        }
        self.ddb.put_item(self.tasks_table, record)
        return record

    def get_email_signals(self, org_id: str) -> List[Dict[str, Any]]:
        """Get all email signals for an org."""
        signals = self.ddb.query_signals(org_id)
        return [s for s in signals if s.get("signal_type") == "email"]

    def generate_reply(self, org_id: str, signal_id: str, tone: str = "professional") -> str:
        """Generate a draft reply for an email signal."""
        signal = self.ddb.get_signal(org_id, signal_id)
        if not signal:
            raise ValueError(f"Signal {signal_id} not found")

        content = signal.get("content", {})
        return self.agent.generate_reply_draft(
            subject=content.get("subject", ""),
            body=content.get("body", ""),
            sender=content.get("sender", ""),
            tone=tone,
        )


import threading


_email_task_service: Optional[EmailTaskService] = None
_ets_lock = threading.Lock()


def get_email_task_service() -> EmailTaskService:
    """Get singleton EmailTaskService instance (thread-safe)."""
    global _email_task_service
    if _email_task_service is None:
        with _ets_lock:
            if _email_task_service is None:
                _email_task_service = EmailTaskService(get_ddb_service())
    return _email_task_service
