from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt, ExpiredSignatureError

from app.auth import hash_password, verify_password, create_access_token
from app.config import Settings

settings = Settings()


def test_hash_returns_string_not_equal_to_password():
    password = "mysecretpassword"
    hashed = hash_password(password)
    assert isinstance(hashed, str)
    assert hashed != password


def test_verify_password_correct():
    hashed = hash_password("mysecretpassword")
    assert verify_password("mysecretpassword", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("mysecretpassword")
    assert verify_password("wrongpassword", hashed) is False


def test_token_has_three_dot_separated_parts():
    token = create_access_token({"sub": "david"})
    assert len(token.split(".")) == 3


def test_token_decodes_back_to_original_claims():
    token = create_access_token({"sub": "david"})
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    assert payload["sub"] == "david"
    assert "exp" in payload


def test_expired_token_raises_error():
    expired = datetime.now(timezone.utc) - timedelta(minutes=1)
    token = jwt.encode(
        {"sub": "david", "exp": expired},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    with pytest.raises(ExpiredSignatureError):
        jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
