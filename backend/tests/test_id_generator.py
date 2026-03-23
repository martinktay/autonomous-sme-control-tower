"""Unit tests for ID Generator utility."""

import pytest
from app.utils.id_generator import generate_id, PREFIXES


class TestGenerateId:
    def test_signal_prefix(self):
        id_ = generate_id("signal")
        assert id_.startswith("sig-")

    def test_transaction_prefix(self):
        id_ = generate_id("transaction")
        assert id_.startswith("txn-")

    def test_subscription_prefix(self):
        id_ = generate_id("subscription")
        assert id_.startswith("sub-")

    def test_org_prefix(self):
        id_ = generate_id("org")
        assert id_.startswith("org-")

    def test_user_prefix(self):
        id_ = generate_id("user")
        assert id_.startswith("usr-")

    def test_unknown_entity_raises(self):
        with pytest.raises(ValueError, match="Unknown entity type"):
            generate_id("spaceship")

    def test_ids_are_unique(self):
        ids = {generate_id("signal") for _ in range(100)}
        assert len(ids) == 100

    def test_id_format(self):
        id_ = generate_id("invoice")
        parts = id_.split("-")
        assert len(parts) == 2
        assert parts[0] == "inv"
        assert len(parts[1]) == 12

    def test_all_prefixes_generate_valid_ids(self):
        for entity in PREFIXES:
            id_ = generate_id(entity)
            prefix = PREFIXES[entity]
            assert id_.startswith(f"{prefix}-")
            assert len(id_) == len(prefix) + 1 + 12
