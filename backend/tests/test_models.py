"""
Unit tests for Pydantic data models

Tests Requirements 1.2, 2.2, 5.5:
- Field validation and type constraints
- Edge cases for numeric ranges (BSI 0-100, confidence 0-1)
- Datetime serialization and deserialization
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from app.models.invoice import Invoice
from app.models.email import Email
from app.models.signal import Signal
from app.models.bsi import BSISnapshot
from app.models.strategy import Strategy
from app.models.action import ActionExecution
from app.models.evaluation import Evaluation


class TestInvoiceModel:
    """Test suite for Invoice model"""
    
    def test_valid_invoice(self):
        """Test creating a valid invoice"""
        invoice = Invoice(
            invoice_id="INV-001",
            org_id="org_123",
            vendor_name="Acme Corp",
            amount=1500.00,
            currency="USD",
            due_date=datetime(2024, 12, 31),
            description="Monthly services",
            status="pending",
            created_at=datetime.now(timezone.utc)
        )
        
        assert invoice.invoice_id == "INV-001"
        assert invoice.amount == 1500.00
        assert invoice.status == "pending"
    
    def test_invoice_missing_required_field(self):
        """Test that missing required fields raise ValidationError"""
        with pytest.raises(ValidationError):
            Invoice(
                invoice_id="INV-001",
                org_id="org_123",
                # Missing vendor_name
                amount=1500.00,
                currency="USD",
                due_date=datetime(2024, 12, 31),
                description="Test"
            )

    def test_invoice_negative_amount(self):
        """Test that negative amounts are rejected"""
        with pytest.raises(ValidationError):
            Invoice(
                invoice_id="INV-001",
                org_id="org_123",
                vendor_name="Acme Corp",
                amount=-100.00,  # Invalid negative amount
                currency="USD",
                due_date=datetime(2024, 12, 31),
                description="Test"
            )
    
    def test_invoice_datetime_serialization(self):
        """Test datetime serialization"""
        now = datetime.now(timezone.utc)
        invoice = Invoice(
            invoice_id="INV-001",
            org_id="org_123",
            vendor_name="Acme Corp",
            amount=1500.00,
            currency="USD",
            due_date=now,
            description="Test",
            created_at=now
        )
        
        # Serialize to dict
        invoice_dict = invoice.model_dump()
        assert isinstance(invoice_dict["due_date"], datetime)
        assert isinstance(invoice_dict["created_at"], datetime)


class TestEmailModel:
    """Test suite for Email model"""
    
    def test_valid_email(self):
        """Test creating a valid email"""
        email = Email(
            email_id="email_001",
            org_id="org_123",
            sender="customer@example.com",
            subject="Payment reminder",
            classification="payment_reminder",
            content="Please pay your invoice",
            created_at=datetime.now(timezone.utc)
        )
        
        assert email.classification == "payment_reminder"
        assert email.sender == "customer@example.com"
    
    def test_email_valid_classifications(self):
        """Test all valid email classifications"""
        valid_classifications = [
            "payment_reminder",
            "customer_inquiry",
            "operational_message",
            "other"
        ]
        
        for classification in valid_classifications:
            email = Email(
                email_id="email_001",
                org_id="org_123",
                sender="test@example.com",
                subject="Test",
                classification=classification,
                content="Test content",
                created_at=datetime.now(timezone.utc)
            )
            assert email.classification == classification


class TestBSISnapshotModel:
    """Test suite for BSISnapshot model"""
    
    def test_valid_bsi_snapshot(self):
        """Test creating a valid BSI snapshot"""
        bsi = BSISnapshot(
            bsi_id="bsi_001",
            org_id="org_123",
            bsi_score=75.5,
            liquidity_index=80.0,
            revenue_stability_index=70.0,
            operational_latency_index=75.0,
            vendor_risk_index=78.0,
            confidence="high",
            reasoning={"cash_runway_risk": "Low risk"},
            timestamp=datetime.now(timezone.utc)
        )
        
        assert bsi.bsi_score == 75.5
        assert bsi.confidence == "high"
    
    def test_bsi_score_bounds(self):
        """Test BSI score must be between 0 and 100"""
        # Valid edge cases
        bsi_min = BSISnapshot(
            bsi_id="bsi_001",
            org_id="org_123",
            bsi_score=0.0,  # Minimum valid
            liquidity_index=0.0,
            revenue_stability_index=0.0,
            operational_latency_index=0.0,
            vendor_risk_index=0.0,
            confidence="low",
            reasoning={},
            timestamp=datetime.now(timezone.utc)
        )
        assert bsi_min.bsi_score == 0.0
        
        bsi_max = BSISnapshot(
            bsi_id="bsi_002",
            org_id="org_123",
            bsi_score=100.0,  # Maximum valid
            liquidity_index=100.0,
            revenue_stability_index=100.0,
            operational_latency_index=100.0,
            vendor_risk_index=100.0,
            confidence="high",
            reasoning={},
            timestamp=datetime.now(timezone.utc)
        )
        assert bsi_max.bsi_score == 100.0
        
        # Invalid: below 0
        with pytest.raises(ValidationError):
            BSISnapshot(
                bsi_id="bsi_003",
                org_id="org_123",
                bsi_score=-1.0,  # Invalid
                liquidity_index=50.0,
                revenue_stability_index=50.0,
                operational_latency_index=50.0,
                vendor_risk_index=50.0,
                confidence="low",
                reasoning={},
                timestamp=datetime.now(timezone.utc)
            )
        
        # Invalid: above 100
        with pytest.raises(ValidationError):
            BSISnapshot(
                bsi_id="bsi_004",
                org_id="org_123",
                bsi_score=101.0,  # Invalid
                liquidity_index=50.0,
                revenue_stability_index=50.0,
                operational_latency_index=50.0,
                vendor_risk_index=50.0,
                confidence="low",
                reasoning={},
                timestamp=datetime.now(timezone.utc)
            )


class TestStrategyModel:
    """Test suite for Strategy model"""
    
    def test_valid_strategy(self):
        """Test creating a valid strategy"""
        strategy = Strategy(
            strategy_id="strat_001",
            org_id="org_123",
            bsi_snapshot_id="bsi_001",
            description="Accelerate invoice collections",
            predicted_bsi_improvement=5.5,
            confidence_score=0.85,
            automation_eligibility=True,
            reasoning="High confidence based on historical data",
            created_at=datetime.now(timezone.utc)
        )
        
        assert strategy.confidence_score == 0.85
        assert strategy.automation_eligibility is True
    
    def test_confidence_score_bounds(self):
        """Test confidence score must be between 0 and 1"""
        # Valid edge cases
        strategy_min = Strategy(
            strategy_id="strat_001",
            org_id="org_123",
            bsi_snapshot_id="bsi_001",
            description="Test",
            predicted_bsi_improvement=5.0,
            confidence_score=0.0,  # Minimum valid
            automation_eligibility=False,
            reasoning="Test",
            created_at=datetime.now(timezone.utc)
        )
        assert strategy_min.confidence_score == 0.0
        
        strategy_max = Strategy(
            strategy_id="strat_002",
            org_id="org_123",
            bsi_snapshot_id="bsi_001",
            description="Test",
            predicted_bsi_improvement=5.0,
            confidence_score=1.0,  # Maximum valid
            automation_eligibility=True,
            reasoning="Test",
            created_at=datetime.now(timezone.utc)
        )
        assert strategy_max.confidence_score == 1.0
        
        # Invalid: below 0
        with pytest.raises(ValidationError):
            Strategy(
                strategy_id="strat_003",
                org_id="org_123",
                bsi_snapshot_id="bsi_001",
                description="Test",
                predicted_bsi_improvement=5.0,
                confidence_score=-0.1,  # Invalid
                automation_eligibility=False,
                reasoning="Test",
                created_at=datetime.now(timezone.utc)
            )
        
        # Invalid: above 1
        with pytest.raises(ValidationError):
            Strategy(
                strategy_id="strat_004",
                org_id="org_123",
                bsi_snapshot_id="bsi_001",
                description="Test",
                predicted_bsi_improvement=5.0,
                confidence_score=1.5,  # Invalid
                automation_eligibility=False,
                reasoning="Test",
                created_at=datetime.now(timezone.utc)
            )


class TestActionExecutionModel:
    """Test suite for ActionExecution model"""
    
    def test_valid_action_execution(self):
        """Test creating a valid action execution"""
        action = ActionExecution(
            execution_id="exec_001",
            org_id="org_123",
            strategy_id="strat_001",
            action_type="update_invoice_status",
            target_entity="INV-001",
            execution_status="success",
            timestamp=datetime.now(timezone.utc)
        )
        
        assert action.execution_status == "success"
        assert action.action_type == "update_invoice_status"
    
    def test_action_execution_with_error(self):
        """Test action execution with error reason"""
        action = ActionExecution(
            execution_id="exec_002",
            org_id="org_123",
            strategy_id="strat_001",
            action_type="update_invoice_status",
            target_entity="INV-001",
            execution_status="failed",
            error_reason="Invoice not found",
            timestamp=datetime.now(timezone.utc)
        )
        
        assert action.execution_status == "failed"
        assert action.error_reason == "Invoice not found"


class TestEvaluationModel:
    """Test suite for Evaluation model"""
    
    def test_valid_evaluation(self):
        """Test creating a valid evaluation"""
        evaluation = Evaluation(
            evaluation_id="eval_001",
            org_id="org_123",
            execution_id="exec_001",
            old_bsi=65.0,
            new_bsi=70.5,
            predicted_improvement=5.0,
            actual_improvement=5.5,
            prediction_accuracy=0.90,
            timestamp=datetime.now(timezone.utc)
        )
        
        assert evaluation.actual_improvement == 5.5
        assert evaluation.prediction_accuracy == 0.90
    
    def test_evaluation_calculation(self):
        """Test evaluation with calculated improvements"""
        old_bsi = 60.0
        new_bsi = 68.0
        predicted_improvement = 10.0
        actual_improvement = new_bsi - old_bsi  # 8.0
        
        evaluation = Evaluation(
            evaluation_id="eval_002",
            org_id="org_123",
            execution_id="exec_001",
            old_bsi=old_bsi,
            new_bsi=new_bsi,
            predicted_improvement=predicted_improvement,
            actual_improvement=actual_improvement,
            prediction_accuracy=0.80,
            timestamp=datetime.now(timezone.utc)
        )
        
        assert evaluation.actual_improvement == 8.0
        assert evaluation.old_bsi < evaluation.new_bsi


class TestSignalModel:
    """Test suite for Signal model"""
    
    def test_valid_signal(self):
        """Test creating a valid signal"""
        signal = Signal(
            signal_id="sig_001",
            org_id="org_123",
            signal_type="invoice",
            content={"invoice_id": "INV-001", "amount": 1500.00},
            created_at=datetime.now(timezone.utc),
            processing_status="processed"
        )
        
        assert signal.signal_type == "invoice"
        assert signal.processing_status == "processed"
    
    def test_signal_with_embedding(self):
        """Test signal with embedding reference"""
        signal = Signal(
            signal_id="sig_002",
            org_id="org_123",
            signal_type="email",
            content={"subject": "Payment reminder"},
            embedding_ref="emb_sig_002",
            created_at=datetime.now(timezone.utc),
            processing_status="processed"
        )
        
        assert signal.embedding_ref == "emb_sig_002"
