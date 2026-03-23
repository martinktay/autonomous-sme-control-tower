"""Unit tests for Upload Validator utility."""

import pytest
from unittest.mock import AsyncMock, Mock
from fastapi import HTTPException
from app.utils.upload_validator import (
    validate_org_id, sanitize_filename,
    validate_upload_file, INVOICE_EXTENSIONS, FINANCE_EXTENSIONS,
    INVOICE_CONTENT_TYPES, FINANCE_CONTENT_TYPES,
)


class TestValidateOrgId:
    def test_valid_org_id(self):
        assert validate_org_id("org-abc123") == "org-abc123"

    def test_valid_org_id_with_underscore(self):
        assert validate_org_id("my_org_1") == "my_org_1"

    def test_empty_org_id_raises(self):
        with pytest.raises(HTTPException) as exc_info:
            validate_org_id("")
        assert exc_info.value.status_code == 400

    def test_none_org_id_raises(self):
        with pytest.raises(HTTPException):
            validate_org_id(None)

    def test_numeric_start_raises(self):
        with pytest.raises(HTTPException):
            validate_org_id("123abc")

    def test_too_long_raises(self):
        with pytest.raises(HTTPException):
            validate_org_id("a" * 100)

    def test_strips_whitespace(self):
        assert validate_org_id("  org-test  ") == "org-test"


class TestSanitizeFilename:
    def test_normal_filename(self):
        assert sanitize_filename("invoice.pdf") == "invoice.pdf"

    def test_path_traversal_stripped(self):
        result = sanitize_filename("../../etc/passwd")
        assert ".." not in result
        assert "/" not in result

    def test_backslash_stripped(self):
        result = sanitize_filename("C:\\Users\\file.pdf")
        assert "\\" not in result

    def test_empty_filename(self):
        assert sanitize_filename("") == "unnamed_file"

    def test_special_characters_replaced(self):
        result = sanitize_filename("my file (1).pdf")
        assert "(" not in result
        assert " " not in result

    def test_long_filename_truncated(self):
        result = sanitize_filename("a" * 300 + ".pdf")
        assert len(result) <= 255


class TestValidateUploadFile:
    @pytest.mark.asyncio
    async def test_valid_pdf_upload(self):
        file = AsyncMock()
        file.content_type = "application/pdf"
        file.filename = "invoice.pdf"
        file.read = AsyncMock(return_value=b"%PDF-1.4 fake content here")

        content, name, ext = await validate_upload_file(
            file, INVOICE_CONTENT_TYPES, INVOICE_EXTENSIONS,
        )
        assert ext == ".pdf"
        assert name == "invoice.pdf"

    @pytest.mark.asyncio
    async def test_valid_csv_upload(self):
        file = AsyncMock()
        file.content_type = "text/csv"
        file.filename = "data.csv"
        file.read = AsyncMock(return_value=b"date,amount\n2025-01-01,5000")

        content, name, ext = await validate_upload_file(
            file, FINANCE_CONTENT_TYPES, FINANCE_EXTENSIONS,
        )
        assert ext == ".csv"

    @pytest.mark.asyncio
    async def test_unsupported_type_raises(self):
        file = AsyncMock()
        file.content_type = "application/zip"
        file.filename = "archive.zip"
        file.read = AsyncMock(return_value=b"PK\x03\x04")

        with pytest.raises(HTTPException) as exc_info:
            await validate_upload_file(file, INVOICE_CONTENT_TYPES, INVOICE_EXTENSIONS)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_empty_file_raises(self):
        file = AsyncMock()
        file.content_type = "application/pdf"
        file.filename = "empty.pdf"
        file.read = AsyncMock(return_value=b"")

        with pytest.raises(HTTPException) as exc_info:
            await validate_upload_file(file, INVOICE_CONTENT_TYPES, INVOICE_EXTENSIONS)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_oversized_file_raises(self):
        file = AsyncMock()
        file.content_type = "application/pdf"
        file.filename = "huge.pdf"
        file.read = AsyncMock(return_value=b"%PDF" + b"x" * (11 * 1024 * 1024))

        with pytest.raises(HTTPException) as exc_info:
            await validate_upload_file(file, INVOICE_CONTENT_TYPES, INVOICE_EXTENSIONS, max_size=10*1024*1024)
        assert exc_info.value.status_code == 413
