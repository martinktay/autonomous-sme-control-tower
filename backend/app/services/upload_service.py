"""
Upload service — manages upload job lifecycle, file parsing, and field mapping.

Handles CSV, Excel, PDF, and image uploads. Coordinates with the mapping agent
for AI-powered column-to-field mapping.
"""

import csv
import io
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.config import get_settings
from app.models.upload_job import UploadJob, UploadJobStatus
from app.services.ddb_service import get_ddb_service
from app.utils.id_generator import generate_id

logger = logging.getLogger(__name__)
settings = get_settings()


class UploadService:
    """Manages the upload job lifecycle from file receipt to processed records."""

    def __init__(self):
        self.ddb = get_ddb_service()
        self.table = settings.upload_jobs_table

    def create_job(
        self,
        business_id: str,
        filename: str,
        file_type: str,
        file_size: int,
        source_channel: str = "manual_upload",
    ) -> UploadJob:
        """Create a new upload job record."""
        now = datetime.now(timezone.utc)
        job = UploadJob(
            job_id=generate_id("upload_job"),
            business_id=business_id,
            filename=filename,
            file_type=file_type,
            file_size_bytes=file_size,
            source_channel=source_channel,
            status=UploadJobStatus.pending,
            created_at=now,
        )
        self.ddb.put_item(self.table, {
            "business_id": job.business_id,
            "job_id": job.job_id,
            **job.model_dump(mode="json"),
        })
        logger.info("Created upload job %s for business %s", job.job_id, business_id)
        return job

    def get_job(self, business_id: str, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an upload job."""
        return self.ddb.get_item(self.table, {
            "business_id": {"S": business_id},
            "job_id": {"S": job_id},
        })

    def list_jobs(self, business_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """List upload jobs for a business."""
        return self.ddb.query_items(
            table_name=self.table,
            key_condition="org_id = :bid",
            expression_values={":bid": business_id},
            limit=limit,
            scan_forward=False,
        )

    def update_job_status(
        self,
        business_id: str,
        job_id: str,
        status: str,
        extra_attrs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update job status and optional attributes."""
        updates = {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}
        if extra_attrs:
            updates.update(extra_attrs)

        expr_parts = []
        expr_values = {}
        expr_names = {}
        for i, (key, value) in enumerate(updates.items()):
            attr_name = f"#a{i}"
            attr_val = f":v{i}"
            expr_parts.append(f"{attr_name} = {attr_val}")
            expr_names[attr_name] = key
            expr_values[attr_val] = self.ddb._convert_to_dynamodb_format({attr_val: value})[attr_val]

        try:
            self.ddb.client.update_item(
                TableName=self.table,
                Key={
                    "business_id": {"S": business_id},
                    "job_id": {"S": job_id},
                },
                UpdateExpression="SET " + ", ".join(expr_parts),
                ExpressionAttributeNames=expr_names,
                ExpressionAttributeValues=expr_values,
            )
        except Exception as e:
            logger.error("Failed to update upload job %s: %s", job_id, e)
            raise

    def parse_csv(self, content: bytes) -> tuple[List[str], List[List[str]]]:
        """Parse CSV content into headers and rows."""
        text = content.decode("utf-8-sig")
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
        if not rows:
            return [], []
        headers = [h.strip() for h in rows[0]]
        data_rows = rows[1:]
        return headers, data_rows

    def parse_excel(self, content: bytes) -> tuple[List[str], List[List[str]]]:
        """Parse Excel content into headers and rows."""
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        ws = wb.active
        rows = []
        for row in ws.iter_rows(values_only=True):
            rows.append([str(cell) if cell is not None else "" for cell in row])
        wb.close()
        if not rows:
            return [], []
        headers = [h.strip() for h in rows[0]]
        data_rows = rows[1:]
        return headers, data_rows


def get_upload_service() -> UploadService:
    return UploadService()
