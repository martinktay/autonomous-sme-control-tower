"""
Shared upload validation utilities for production-safe file handling.

Validates file size, content type, filename, and org_id before processing.
"""

import re
import logging
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

# Limits
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_FILENAME_LENGTH = 255

# Allowed MIME types by upload context
INVOICE_CONTENT_TYPES = {"application/pdf", "image/jpeg", "image/png", "image/jpg"}
FINANCE_CONTENT_TYPES = INVOICE_CONTENT_TYPES | {
    "text/csv", "application/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
INVOICE_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
FINANCE_EXTENSIONS = INVOICE_EXTENSIONS | {".csv", ".xls", ".xlsx"}

# org_id pattern — must start with a letter, 2-65 chars, alphanumeric/dash/underscore
_ORG_ID_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{1,64}$")

# Dangerous filename characters
_UNSAFE_FILENAME_RE = re.compile(r"[^\w.\-]")


def validate_org_id(org_id: str) -> str:
    """Validate and return sanitized org_id. Raises HTTPException 400 on failure."""
    if not org_id or not isinstance(org_id, str):
        raise HTTPException(400, "org_id is required.")
    org_id = org_id.strip()
    if not _ORG_ID_RE.match(org_id):
        raise HTTPException(400, "Invalid org_id format. Must start with a letter and contain only letters, numbers, dashes, or underscores (2-65 chars).")
    return org_id


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and injection attacks."""
    if not filename:
        return "unnamed_file"
    # Strip path separators
    filename = filename.replace("/", "_").replace("\\", "_")
    # Remove any directory traversal
    filename = filename.replace("..", "_")
    # Replace unsafe characters
    name_parts = filename.rsplit(".", 1)
    if len(name_parts) == 2:
        base = _UNSAFE_FILENAME_RE.sub("_", name_parts[0])
        ext = _UNSAFE_FILENAME_RE.sub("_", name_parts[1])
        filename = f"{base}.{ext}"
    else:
        filename = _UNSAFE_FILENAME_RE.sub("_", filename)
    # Truncate
    if len(filename) > MAX_FILENAME_LENGTH:
        filename = filename[:MAX_FILENAME_LENGTH]
    return filename


async def validate_upload_file(
    file: UploadFile,
    allowed_types: set[str],
    allowed_extensions: set[str],
    max_size: int = MAX_FILE_SIZE_BYTES,
) -> tuple[bytes, str, str]:
    """
    Validate and read an uploaded file.

    Returns:
        (file_content, sanitized_filename, detected_extension)

    Raises:
        HTTPException 400 for invalid file type/name
        HTTPException 413 for oversized files
    """
    content_type = (file.content_type or "").lower().strip()
    raw_filename = file.filename or "unnamed_file"
    safe_filename = sanitize_filename(raw_filename)

    # Extract extension
    ext = ""
    if "." in safe_filename:
        ext = "." + safe_filename.rsplit(".", 1)[-1].lower()

    # Validate type by content_type or extension
    type_ok = content_type in allowed_types
    ext_ok = ext in allowed_extensions
    if not type_ok and not ext_ok:
        allowed = ", ".join(sorted(allowed_extensions))
        raise HTTPException(400, f"Unsupported file type. Accepted formats: {allowed}")

    # Read content
    file_content = await file.read()

    # Validate not empty
    if len(file_content) == 0:
        raise HTTPException(400, "Uploaded file is empty.")

    # Validate size
    if len(file_content) > max_size:
        max_mb = max_size / (1024 * 1024)
        raise HTTPException(413, f"File exceeds the {max_mb:.0f} MB size limit.")

    # Basic magic-byte validation for PDFs
    if ext == ".pdf" or "pdf" in content_type:
        if not file_content[:5].startswith(b"%PDF"):
            logger.warning(f"File {safe_filename} claims PDF but lacks PDF header")
            # Allow it through — some PDFs have BOM or whitespace prefix

    return file_content, safe_filename, ext
