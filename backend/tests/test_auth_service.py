"""Unit tests for Auth Service — JWT helpers and password hashing."""

import pytest
from unittest.mock import patch
from app.services.auth_service import (
    _hash_password, _verify_password,
    create_access_token, decode_access_token,
)


class TestPasswordHashing:
    def test_hash_and_verify_correct_password(self):
        pw_hash, salt = _hash_password("mysecretpassword")
        assert _verify_password("mysecretpassword", pw_hash, salt) is True

    def test_verify_wrong_password(self):
        pw_hash, salt = _hash_password("correct")
        assert _verify_password("wrong", pw_hash, salt) is False

    def test_hash_produces_different_salts(self):
        _, salt1 = _hash_password("password")
        _, salt2 = _hash_password("password")
        assert salt1 != salt2

    def test_hash_with_explicit_salt(self):
        h1, _ = _hash_password("test", salt="fixed-salt")
        h2, _ = _hash_password("test", salt="fixed-salt")
        assert h1 == h2

    def test_hash_returns_hex_strings(self):
        pw_hash, salt = _hash_password("test")
        assert isinstance(pw_hash, str)
        assert isinstance(salt, str)
        int(pw_hash, 16)  # should not raise
        int(salt, 16)


class TestJWT:
    def test_create_and_decode_token(self):
        data = {"sub": "user-123", "email": "test@example.com", "org_id": "org-456", "role": "owner"}
        token = create_access_token(data, expires_hours=1)

        claims = decode_access_token(token)
        assert claims is not None
        assert claims["sub"] == "user-123"
        assert claims["org_id"] == "org-456"

    def test_decode_invalid_token_returns_none(self):
        assert decode_access_token("invalid.token.here") is None

    def test_decode_empty_token_returns_none(self):
        assert decode_access_token("") is None

    def test_token_contains_exp_and_iat(self):
        token = create_access_token({"sub": "u1"}, expires_hours=1)
        claims = decode_access_token(token)
        assert "exp" in claims
        assert "iat" in claims

    def test_token_with_custom_expiry(self):
        token = create_access_token({"sub": "u1"}, expires_hours=24)
        claims = decode_access_token(token)
        assert claims is not None
        # exp should be roughly 24h from iat
        assert claims["exp"] - claims["iat"] >= 86000

    def test_tampered_token_returns_none(self):
        token = create_access_token({"sub": "u1"})
        # Tamper with the payload
        parts = token.split(".")
        parts[1] = parts[1][::-1]  # reverse payload
        tampered = ".".join(parts)
        assert decode_access_token(tampered) is None
