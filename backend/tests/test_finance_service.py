"""
Unit tests for Finance Document model, agent, and service.
Tests Requirements 9.7, 12.6, 13.1-13.6
"""

import csv
import io
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from app.models.finance_document import FinanceDocument, DocumentFlag
from app.agents.finance_agent import FinanceDocumentAgent
from app.services.finance_service import FinanceService


def _make_doc(overrides=None):
    base = {
        "document_id": "doc-1",
        "org_id": "org-1",
        "vendor_name": "Acme",
        "amount": 100.0,
        "currency": "USD",
        "document_date": datetime(2025, 1, 15),
        "description": "Test invoice",
        "category": "expense",
        "confidence_score": 0.9,
        "s3_key": "documents/org-1/doc-1/file.pdf",
    }
    if overrides:
        base.update(overrides)
    return base


def _make_signal(content_overrides=None, signal_id="sig-1"):
    content = {
        "document_id": "doc-1",
        "vendor_name": "Acme",
        "amount": 100.0,
        "currency": "USD",
        "document_date": "2025-01-15",
        "category": "expense",
        "confidence_score": 0.9,
        "processing_status": "processed",
        "vat_amount": 0,
        "vat_rate": 0,
    }
    if content_overrides:
        content.update(content_overrides)
    return {
        "signal_id": signal_id,
        "org_id": "org-1",
        "signal_type": "finance_document",
        "content": content,
    }


# ==================== 1. FinanceDocument Model Validators ====================

class TestFinanceDocumentModel:

    def test_valid_document(self):
        doc = FinanceDocument(**_make_doc())
        assert doc.amount == 100.0

    def test_valid_currency_codes(self):
        for code in ("USD", "GBP", "NGN", "EUR"):
            doc = FinanceDocument(**_make_doc({"currency": code}))
            assert doc.currency == code

    def test_invalid_currency_lowercase(self):
        with pytest.raises(ValidationError):
            FinanceDocument(**_make_doc({"currency": "usd"}))

    def test_invalid_currency_length(self):
        with pytest.raises(ValidationError):
            FinanceDocument(**_make_doc({"currency": "US"}))

    def test_invalid_currency_numeric(self):
        with pytest.raises(ValidationError):
            FinanceDocument(**_make_doc({"currency": "U2D"}))

    def test_valid_categories(self):
        for cat in ("revenue", "expense"):
            doc = FinanceDocument(**_make_doc({"category": cat}))
            assert doc.category == cat

    def test_invalid_category(self):
        with pytest.raises(ValidationError):
            FinanceDocument(**_make_doc({"category": "other"}))

    def test_valid_statuses(self):
        for status in ("processed", "needs_review", "approved", "rejected", "failed"):
            doc = FinanceDocument(**_make_doc({"processing_status": status}))
            assert doc.processing_status == status

    def test_invalid_status(self):
        with pytest.raises(ValidationError):
            FinanceDocument(**_make_doc({"processing_status": "pending"}))

    def test_amount_must_be_positive(self):
        with pytest.raises(ValidationError):
            FinanceDocument(**_make_doc({"amount": 0}))
        with pytest.raises(ValidationError):
            FinanceDocument(**_make_doc({"amount": -10}))

    def test_confidence_score_bounds(self):
        FinanceDocument(**_make_doc({"confidence_score": 0.0}))
        FinanceDocument(**_make_doc({"confidence_score": 1.0}))
        with pytest.raises(ValidationError):
            FinanceDocument(**_make_doc({"confidence_score": -0.1}))
        with pytest.raises(ValidationError):
            FinanceDocument(**_make_doc({"confidence_score": 1.1}))

    def test_vat_amount_nonnegative(self):
        doc = FinanceDocument(**_make_doc({"vat_amount": 0.0}))
        assert doc.vat_amount == 0.0
        doc2 = FinanceDocument(**_make_doc({"vat_amount": 20.0}))
        assert doc2.vat_amount == 20.0
        with pytest.raises(ValidationError):
            FinanceDocument(**_make_doc({"vat_amount": -1.0}))

    def test_vat_rate_nonnegative(self):
        doc = FinanceDocument(**_make_doc({"vat_rate": 0.0}))
        assert doc.vat_rate == 0.0
        with pytest.raises(ValidationError):
            FinanceDocument(**_make_doc({"vat_rate": -5.0}))

    def test_vat_fields_optional(self):
        doc = FinanceDocument(**_make_doc())
        assert doc.vat_amount is None
        assert doc.vat_rate is None

    def test_flags_field(self):
        flags = [DocumentFlag(flag_type="duplicate", flag_reason="dup")]
        doc = FinanceDocument(**_make_doc({"flags": flags}))
        assert len(doc.flags) == 1
        assert doc.flags[0].flag_type == "duplicate"


# ==================== 2. FinanceDocumentAgent ====================

class TestFinanceDocumentAgent:

    @patch("app.agents.finance_agent.get_bedrock_client")
    @patch("app.agents.finance_agent.load_prompt", return_value="prompt")
    @patch("app.agents.finance_agent.parse_json_safely")
    def test_extract_document(self, mock_parse, mock_prompt, mock_bedrock_factory):
        mock_client = MagicMock()
        mock_client.invoke_nova_lite.return_value = '{"vendor_name":"Acme"}'
        mock_bedrock_factory.return_value = mock_client
        mock_parse.return_value = {"vendor_name": "Acme", "amount": 100}
        agent = FinanceDocumentAgent()
        result = agent.extract_document("raw text", currency_hint="USD")
        assert result["vendor_name"] == "Acme"
        mock_client.invoke_nova_lite.assert_called_once()

    @patch("app.agents.finance_agent.get_bedrock_client")
    @patch("app.agents.finance_agent.load_prompt", return_value="prompt")
    @patch("app.agents.finance_agent.parse_json_safely")
    def test_classify_document(self, mock_parse, mock_prompt, mock_bedrock_factory):
        mock_client = MagicMock()
        mock_client.invoke_nova_lite.return_value = '{"category":"revenue"}'
        mock_bedrock_factory.return_value = mock_client
        mock_parse.return_value = {"category": "revenue", "confidence_score": 0.95}
        agent = FinanceDocumentAgent()
        result = agent.classify_document({"vendor_name": "Acme", "amount": 100})
        assert result["category"] == "revenue"
        assert result["confidence_score"] == 0.95

    @patch("app.agents.finance_agent.get_bedrock_client")
    @patch("app.agents.finance_agent.load_prompt", return_value="prompt")
    @patch("app.agents.finance_agent.parse_json_safely")
    def test_parse_informal_receipt(self, mock_parse, mock_prompt, mock_bedrock_factory):
        mock_client = MagicMock()
        mock_client.invoke_nova_lite.return_value = '{"vendor_name":"Market"}'
        mock_bedrock_factory.return_value = mock_client
        mock_parse.return_value = {"vendor_name": "Market", "amount": 500, "currency": "NGN"}
        agent = FinanceDocumentAgent()
        result = agent.parse_informal_receipt("POS slip text")
        assert result["currency"] == "NGN"


# ==================== 3. FinanceService Core ====================

class TestFinanceServiceCore:

    def _make_service(self, signals=None):
        ddb = MagicMock()
        ddb.query_signals.return_value = signals or []
        return FinanceService(ddb), ddb

    def test_get_finance_documents_filters_type(self):
        svc, _ = self._make_service([
            {"signal_type": "finance_document", "content": {}},
            {"signal_type": "email", "content": {}},
        ])
        docs = svc.get_finance_documents("org-1")
        assert len(docs) == 1

    def test_detect_anomalies_duplicate(self):
        existing = _make_signal({"vendor_name": "Acme", "amount": 100, "document_date": "2025-01-15"})
        svc, _ = self._make_service([existing])
        new_doc = {"content": {"vendor_name": "Acme", "amount": 100, "document_date": "2025-01-15"}}
        flags = svc.detect_anomalies("org-1", new_doc)
        assert any(f.flag_type == "duplicate" for f in flags)

    def test_detect_anomalies_outlier(self):
        # Use varying amounts so stdev > 0; 1000 is well beyond 3 sigma
        signals = [
            _make_signal({"vendor_name": "Acme", "amount": 100}, signal_id="s0"),
            _make_signal({"vendor_name": "Acme", "amount": 105}, signal_id="s1"),
            _make_signal({"vendor_name": "Acme", "amount": 98}, signal_id="s2"),
        ]
        svc, _ = self._make_service(signals)
        new_doc = {"content": {"vendor_name": "Acme", "amount": 1000, "document_date": "2025-02-01"}}
        flags = svc.detect_anomalies("org-1", new_doc)
        assert any(f.flag_type == "anomaly" for f in flags)

    def test_detect_anomalies_no_flags(self):
        existing = _make_signal({"vendor_name": "Acme", "amount": 100, "document_date": "2025-01-15"})
        svc, _ = self._make_service([existing])
        new_doc = {"content": {"vendor_name": "Other", "amount": 200, "document_date": "2025-02-01"}}
        flags = svc.detect_anomalies("org-1", new_doc)
        assert len(flags) == 0

    def test_get_review_queue(self):
        signals = [
            _make_signal({"processing_status": "needs_review"}, signal_id="s1"),
            _make_signal({"processing_status": "approved"}, signal_id="s2"),
        ]
        svc, _ = self._make_service(signals)
        queue = svc.get_review_queue("org-1")
        assert len(queue) == 1

    def test_update_review_approve(self):
        ddb = MagicMock()
        ddb.query_signals.return_value = []
        ddb.get_signal.return_value = {"content": {"processing_status": "needs_review"}}
        svc = FinanceService(ddb)
        svc.update_review_status("org-1", "sig-1", "approve")
        ddb.update_signal.assert_called_once()
        call_args = ddb.update_signal.call_args[0]
        assert call_args[2]["content"]["processing_status"] == "approved"

    def test_update_review_reject(self):
        ddb = MagicMock()
        ddb.get_signal.return_value = {"content": {"processing_status": "needs_review"}}
        svc = FinanceService(ddb)
        svc.update_review_status("org-1", "sig-1", "reject")
        call_args = ddb.update_signal.call_args[0]
        assert call_args[2]["content"]["processing_status"] == "rejected"

    def test_update_review_edit(self):
        ddb = MagicMock()
        ddb.get_signal.return_value = {"content": {"processing_status": "needs_review", "vendor_name": "Old"}}
        svc = FinanceService(ddb)
        svc.update_review_status("org-1", "sig-1", "edit", {"vendor_name": "New"})
        call_args = ddb.update_signal.call_args[0]
        assert call_args[2]["content"]["vendor_name"] == "New"
        assert call_args[2]["content"]["processing_status"] == "approved"

    def test_update_review_invalid_action(self):
        ddb = MagicMock()
        ddb.get_signal.return_value = {"content": {}}
        svc = FinanceService(ddb)
        with pytest.raises(ValueError, match="Invalid action"):
            svc.update_review_status("org-1", "sig-1", "invalid")

    def test_update_review_not_found(self):
        ddb = MagicMock()
        ddb.get_signal.return_value = None
        svc = FinanceService(ddb)
        with pytest.raises(ValueError, match="not found"):
            svc.update_review_status("org-1", "sig-1", "approve")


# ==================== 4. Cashflow & P&L ====================

class TestFinanceServiceCashflowPnl:

    def _svc_with_docs(self, docs):
        ddb = MagicMock()
        ddb.query_signals.return_value = docs
        return FinanceService(ddb)

    def test_cashflow_monthly_aggregation(self):
        docs = [
            _make_signal({"category": "revenue", "amount": 500, "document_date": "2025-01-10", "processing_status": "approved"}, "s1"),
            _make_signal({"category": "expense", "amount": 200, "document_date": "2025-01-20", "processing_status": "processed"}, "s2"),
            _make_signal({"category": "revenue", "amount": 300, "document_date": "2025-02-05", "processing_status": "approved"}, "s3"),
        ]
        svc = self._svc_with_docs(docs)
        result = svc.get_cashflow("org-1", "monthly")
        assert len(result) == 2
        jan = next(r for r in result if r["period"] == "2025-01")
        assert jan["revenue"] == 500.0
        assert jan["expenses"] == 200.0

    def test_cashflow_empty(self):
        svc = self._svc_with_docs([])
        result = svc.get_cashflow("org-1")
        assert result == []

    def test_cashflow_date_filter(self):
        docs = [
            _make_signal({"category": "revenue", "amount": 100, "document_date": "2025-01-10", "processing_status": "approved"}, "s1"),
            _make_signal({"category": "revenue", "amount": 200, "document_date": "2025-03-10", "processing_status": "approved"}, "s2"),
        ]
        svc = self._svc_with_docs(docs)
        result = svc.get_cashflow("org-1", "monthly", start_date="2025-02-01", end_date="2025-04-01")
        assert len(result) == 1
        assert result[0]["revenue"] == 200.0

    def test_cashflow_excludes_rejected(self):
        docs = [
            _make_signal({"category": "revenue", "amount": 100, "document_date": "2025-01-10", "processing_status": "rejected"}, "s1"),
        ]
        svc = self._svc_with_docs(docs)
        result = svc.get_cashflow("org-1")
        assert result == []

    def test_pnl_basic(self):
        docs = [
            _make_signal({"category": "revenue", "amount": 1000, "document_date": "2025-01-10", "processing_status": "approved", "vat_amount": 200}, "s1"),
            _make_signal({"category": "expense", "amount": 400, "document_date": "2025-01-15", "processing_status": "processed", "vat_amount": 80}, "s2"),
        ]
        svc = self._svc_with_docs(docs)
        result = svc.get_pnl("org-1")
        assert result["total_revenue"] == 1000.0
        assert result["total_expenses"] == 400.0
        assert result["net_profit"] == 600.0
        assert result["vat_summary"]["total_vat_collected"] == 200.0
        assert result["vat_summary"]["total_vat_paid"] == 80.0

    def test_pnl_empty(self):
        svc = self._svc_with_docs([])
        result = svc.get_pnl("org-1")
        assert result["total_revenue"] == 0.0
        assert result["net_profit"] == 0.0

    def test_pnl_vendor_breakdown(self):
        docs = [
            _make_signal({"category": "revenue", "amount": 500, "vendor_name": "ClientA", "document_date": "2025-01-10", "processing_status": "approved"}, "s1"),
            _make_signal({"category": "expense", "amount": 200, "vendor_name": "SupplierB", "document_date": "2025-01-15", "processing_status": "approved"}, "s2"),
        ]
        svc = self._svc_with_docs(docs)
        result = svc.get_pnl("org-1")
        assert "ClientA" in result["by_vendor"]
        assert result["by_vendor"]["ClientA"]["revenue"] == 500.0
        assert "SupplierB" in result["by_vendor"]
        assert result["by_vendor"]["SupplierB"]["expenses"] == 200.0


# ==================== 5. Reconciliation ====================

class TestFinanceServiceReconciliation:

    def _svc_with_docs(self, docs):
        ddb = MagicMock()
        ddb.query_signals.return_value = docs
        return FinanceService(ddb)

    def _bank_csv(self, rows):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["date", "description", "amount"])
        for row in rows:
            writer.writerow(row)
        return output.getvalue()

    def test_exact_match(self):
        docs = [
            _make_signal({"vendor_name": "Acme Corp", "amount": 100.0, "document_date": "2025-01-15", "processing_status": "approved"}, "s1"),
        ]
        svc = self._svc_with_docs(docs)
        bank = self._bank_csv([("2025-01-15", "Acme Corp", "100.0")])
        result = svc.reconcile("org-1", bank)
        assert result["summary"]["matched_count"] == 1
        assert result["summary"]["unmatched_transaction_count"] == 0

    def test_amount_within_tolerance(self):
        docs = [
            _make_signal({"vendor_name": "Acme Corp", "amount": 100.0, "document_date": "2025-01-15", "processing_status": "approved"}, "s1"),
        ]
        svc = self._svc_with_docs(docs)
        bank = self._bank_csv([("2025-01-15", "Acme Corp", "100.5")])
        result = svc.reconcile("org-1", bank)
        assert result["summary"]["matched_count"] == 1

    def test_amount_outside_tolerance(self):
        docs = [
            _make_signal({"vendor_name": "Acme Corp", "amount": 100.0, "document_date": "2025-01-15", "processing_status": "approved"}, "s1"),
        ]
        svc = self._svc_with_docs(docs)
        bank = self._bank_csv([("2025-01-15", "Acme Corp", "102.0")])
        result = svc.reconcile("org-1", bank)
        assert result["summary"]["matched_count"] == 0

    def test_date_within_tolerance(self):
        docs = [
            _make_signal({"vendor_name": "Acme Corp", "amount": 100.0, "document_date": "2025-01-15", "processing_status": "approved"}, "s1"),
        ]
        svc = self._svc_with_docs(docs)
        bank = self._bank_csv([("2025-01-18", "Acme Corp", "100.0")])
        result = svc.reconcile("org-1", bank)
        assert result["summary"]["matched_count"] == 1

    def test_date_outside_tolerance(self):
        docs = [
            _make_signal({"vendor_name": "Acme Corp", "amount": 100.0, "document_date": "2025-01-15", "processing_status": "approved"}, "s1"),
        ]
        svc = self._svc_with_docs(docs)
        bank = self._bank_csv([("2025-01-20", "Acme Corp", "100.0")])
        result = svc.reconcile("org-1", bank)
        assert result["summary"]["matched_count"] == 0

    def test_no_matches(self):
        docs = [
            _make_signal({"vendor_name": "Acme Corp", "amount": 100.0, "document_date": "2025-01-15", "processing_status": "approved"}, "s1"),
        ]
        svc = self._svc_with_docs(docs)
        bank = self._bank_csv([("2025-06-01", "Totally Different", "999.0")])
        result = svc.reconcile("org-1", bank)
        assert result["summary"]["matched_count"] == 0
        assert result["summary"]["unmatched_transaction_count"] == 1

    def test_empty_csv(self):
        docs = [
            _make_signal({"vendor_name": "Acme", "amount": 100.0, "document_date": "2025-01-15", "processing_status": "approved"}, "s1"),
        ]
        svc = self._svc_with_docs(docs)
        bank = "date,description,amount\n"
        result = svc.reconcile("org-1", bank)
        assert result["summary"]["total_transactions"] == 0
        assert result["summary"]["matched_count"] == 0


# ==================== 6. CSV Export ====================

class TestFinanceServiceCsvExport:

    def _svc_with_docs(self, docs):
        ddb = MagicMock()
        ddb.query_signals.return_value = docs
        return FinanceService(ddb)

    def test_basic_export(self):
        docs = [
            _make_signal({"vendor_name": "Acme", "amount": 100, "currency": "USD", "document_date": "2025-01-15", "processing_status": "approved", "category": "expense", "confidence_score": 0.9}, "s1"),
        ]
        svc = self._svc_with_docs(docs)
        csv_str = svc.export_csv("org-1")
        reader = csv.DictReader(io.StringIO(csv_str))
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["vendor_name"] == "Acme"
        assert rows[0]["amount"] == "100"

    def test_category_filter(self):
        docs = [
            _make_signal({"category": "revenue", "amount": 500, "document_date": "2025-01-10", "processing_status": "approved"}, "s1"),
            _make_signal({"category": "expense", "amount": 200, "document_date": "2025-01-15", "processing_status": "approved"}, "s2"),
        ]
        svc = self._svc_with_docs(docs)
        csv_str = svc.export_csv("org-1", category="revenue")
        reader = csv.DictReader(io.StringIO(csv_str))
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["category"] == "revenue"

    def test_date_filter(self):
        docs = [
            _make_signal({"amount": 100, "document_date": "2025-01-10", "processing_status": "approved"}, "s1"),
            _make_signal({"amount": 200, "document_date": "2025-03-10", "processing_status": "approved"}, "s2"),
        ]
        svc = self._svc_with_docs(docs)
        csv_str = svc.export_csv("org-1", start_date="2025-02-01", end_date="2025-04-01")
        reader = csv.DictReader(io.StringIO(csv_str))
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["amount"] == "200"

    def test_csv_round_trip(self):
        docs = [
            _make_signal({"vendor_name": "Acme", "amount": 100, "currency": "USD", "document_date": "2025-01-15", "processing_status": "approved", "category": "expense", "confidence_score": 0.9, "vat_amount": 20, "vat_rate": 20}, "s1"),
        ]
        svc = self._svc_with_docs(docs)
        csv_str = svc.export_csv("org-1")
        reader = csv.DictReader(io.StringIO(csv_str))
        rows = list(reader)
        assert float(rows[0]["amount"]) == 100.0
        assert float(rows[0]["vat_amount"]) == 20.0

    def test_empty_export(self):
        svc = self._svc_with_docs([])
        csv_str = svc.export_csv("org-1")
        reader = csv.DictReader(io.StringIO(csv_str))
        rows = list(reader)
        assert len(rows) == 0

    def test_csv_headers(self):
        svc = self._svc_with_docs([])
        csv_str = svc.export_csv("org-1")
        reader = csv.DictReader(io.StringIO(csv_str))
        expected = [
            "document_id", "vendor_name", "amount", "currency",
            "vat_amount", "vat_rate", "wht_amount", "cit_amount",
            "paye_amount", "customs_levy", "document_date", "category",
            "confidence_score", "processing_status",
        ]
        assert reader.fieldnames == expected

