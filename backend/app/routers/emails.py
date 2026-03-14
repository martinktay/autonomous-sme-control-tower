"""
Email ingestion and task management router.

Endpoints cover the full email lifecycle:
- Ingest emails (classify via AI, extract tasks, store as signals)
- List emails and tasks per organisation
- Generate AI-drafted replies
- Send emails via AWS SES
- Manage task status (create, update, filter)
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from app.services.email_task_service import get_email_task_service

router = APIRouter(prefix="/api/emails", tags=["emails"])


# ==================== Request Schemas ====================


class IngestEmailRequest(BaseModel):
    """Payload for ingesting a new business email."""

    org_id: str
    subject: str
    body: str
    sender: str


class CreateTaskRequest(BaseModel):
    """Payload for manually creating a task (not from email)."""

    title: str
    description: str = ""
    task_type: str = "other"
    priority: str = "medium"
    due_date: Optional[str] = None
    assigned_to: Optional[str] = None


class UpdateTaskRequest(BaseModel):
    """Payload for updating a task's status."""

    status: str
    result: Optional[str] = None


class ReplyRequest(BaseModel):
    """Payload for generating a draft reply with a given tone."""

    tone: str = "professional"


class SendReplyRequest(BaseModel):
    """Payload for sending an email via SES."""

    to: str
    subject: str
    body: str
    reply_to: Optional[str] = None


# ==================== SES Endpoints (before parameterized routes) ====================


@router.get("/ses/status")
async def ses_status() -> Dict[str, Any]:
    """Return current SES sending quota (max 24h, sent, rate)."""
    from app.services.ses_service import get_ses_service
    ses = get_ses_service()
    return ses.check_sending_enabled()


@router.post("/ses/verify")
async def verify_sender(email: str) -> Dict[str, Any]:
    """Trigger SES identity verification for sandbox sending."""
    from app.services.ses_service import get_ses_service
    ses = get_ses_service()
    try:
        return ses.verify_email(email)
    except Exception as e:
        raise HTTPException(502, f"Verification failed: {str(e)}")


# ==================== Email Endpoints ====================


@router.post("/ingest")
async def ingest_email(request: IngestEmailRequest) -> Dict[str, Any]:
    """Ingest a business email: AI-classify, extract tasks, persist as signal."""
    svc = get_email_task_service()
    result = svc.ingest_email(
        org_id=request.org_id,
        subject=request.subject,
        body=request.body,
        sender=request.sender,
    )
    return result


@router.get("/{org_id}")
async def get_emails(org_id: str) -> Dict[str, Any]:
    """List all ingested email signals for an org."""
    svc = get_email_task_service()
    emails = svc.get_email_signals(org_id)
    return {"org_id": org_id, "emails": emails}


@router.post("/{org_id}/{signal_id}/reply")
async def generate_reply(org_id: str, signal_id: str, request: ReplyRequest) -> Dict[str, Any]:
    """Use AI to draft a reply for a previously ingested email signal."""
    svc = get_email_task_service()
    try:
        draft = svc.generate_reply(org_id, signal_id, tone=request.tone)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"org_id": org_id, "signal_id": signal_id, "draft_reply": draft}


# ==================== Task Endpoints ====================


@router.get("/{org_id}/tasks")
async def get_tasks(
    org_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
) -> Dict[str, Any]:
    """List tasks for an org with optional status/priority filters."""
    svc = get_email_task_service()
    tasks = svc.get_tasks(org_id, status=status, priority=priority)
    return {"org_id": org_id, "tasks": tasks}


@router.get("/{org_id}/tasks/{task_id}")
async def get_task(org_id: str, task_id: str) -> Dict[str, Any]:
    """Get a single task."""
    svc = get_email_task_service()
    task = svc.get_task(org_id, task_id)
    if not task:
        raise HTTPException(404, f"Task {task_id} not found")
    return task


@router.post("/{org_id}/tasks")
async def create_task(org_id: str, request: CreateTaskRequest) -> Dict[str, Any]:
    """Create a manual task."""
    svc = get_email_task_service()
    task = svc.create_manual_task(org_id, request.model_dump())
    return task


@router.put("/{org_id}/tasks/{task_id}")
async def update_task(org_id: str, task_id: str, request: UpdateTaskRequest) -> Dict[str, Any]:
    """Update task status."""
    svc = get_email_task_service()
    try:
        task = svc.update_task_status(org_id, task_id, request.status, request.result)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return task


# ==================== Email Sending (SES) ====================


@router.post("/{org_id}/send")
async def send_email(org_id: str, request: SendReplyRequest) -> Dict[str, Any]:
    """Send an outbound email via AWS SES on behalf of the organisation."""
    from app.services.ses_service import get_ses_service
    ses = get_ses_service()
    try:
        result = ses.send_email(
            to=request.to,
            subject=request.subject,
            body_text=request.body,
            reply_to=request.reply_to,
        )
        return {"org_id": org_id, **result}
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(502, f"Failed to send email: {str(e)}")

