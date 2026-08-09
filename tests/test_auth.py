"""Tests for authentication utilities (no database needed)."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth import hash_password, verify_password, create_token, verify_token


# --- Password Hashing Tests ---

def test_hash_password_produces_bcrypt_hash():
    """hash_password should return a bcrypt hash starting with $2b$."""
    hashed = hash_password("TestPass123")
    assert hashed.startswith("$2b$")
    assert len(hashed) == 60


def test_verify_password_correct():
    """verify_password should return True for correct password."""
    hashed = hash_password("MyPassword!")
    assert verify_password("MyPassword!", hashed) is True


def test_verify_password_wrong():
    """verify_password should return False for wrong password."""
    hashed = hash_password("MyPassword!")
    assert verify_password("WrongPassword", hashed) is False


def test_verify_password_empty():
    """verify_password should return False for empty string."""
    hashed = hash_password("SomePassword")
    assert verify_password("", hashed) is False


# --- JWT Token Tests ---

def test_create_token_returns_string():
    """create_token should return a non-empty string."""
    token = create_token("user-123", "associate")
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_token_valid():
    """verify_token should decode a valid token correctly."""
    token = create_token("user-abc", "admin")
    payload = verify_token(token)
    assert payload is not None
    assert payload["user_id"] == "user-abc"
    assert payload["role"] == "admin"


def test_verify_token_associate_role():
    """verify_token should return associate role."""
    token = create_token("user-xyz", "associate")
    payload = verify_token(token)
    assert payload["role"] == "associate"


def test_verify_token_invalid():
    """verify_token should return None for an invalid token."""
    result = verify_token("this-is-not-a-valid-token")
    assert result is None


def test_verify_token_tampered():
    """verify_token should return None for a tampered token."""
    token = create_token("user-123", "associate")
    # Tamper with the token
    tampered = token[:-5] + "XXXXX"
    result = verify_token(tampered)
    assert result is None


# --- Admin seed password verification ---

def test_admin_seed_password():
    """Verify the seeded admin password hash matches 'Admin@1234'."""
    seed_hash = "$2b$12$0olMrciiiCPbwGceN6aOiOcGc2MA8JTFAdWHhx/IMFYCiIFm1ILdy"
    assert verify_password("Admin@1234", seed_hash) is True
    assert verify_password("wrong", seed_hash) is False
