"""
Centralized ID generator with entity-specific prefixes.

All IDs follow the pattern: {prefix}-{12_hex_chars}
This ensures IDs are human-readable, sortable by entity type,
and consistent across the entire platform.
"""

import uuid
from typing import Dict

# Entity prefix mapping
PREFIXES: Dict[str, str] = {
    "signal": "sig",
    "transaction": "txn",
    "invoice": "inv",
    "alert": "alt",
    "insight": "ins",
    "counterparty": "ctp",
    "inventory_item": "itm",
    "upload_job": "job",
    "evaluation": "evl",
    "action": "act",
    "strategy": "str",
    "bsi": "bsi",
    "business": "biz",
    "user": "usr",
    "branch": "brn",
    "task": "tsk",
    "email": "eml",
    "document": "doc",
    "org": "org",
    "subscription": "sub",
}


def generate_id(entity: str) -> str:
    """Generate a prefixed ID for the given entity type.

    Args:
        entity: One of the keys in PREFIXES (e.g. 'signal', 'transaction').

    Returns:
        A string like 'sig-a1b2c3d4e5f6'.

    Raises:
        ValueError: If entity is not a recognised type.
    """
    prefix = PREFIXES.get(entity)
    if prefix is None:
        raise ValueError(
            f"Unknown entity type '{entity}'. Valid types: {sorted(PREFIXES.keys())}"
        )
    return f"{prefix}-{uuid.uuid4().hex[:12]}"
