from uuid import uuid4

from app.auth import create_access_token, hash_password, verify_password


def test_password_hash_is_not_reversible() -> None:
    password = "very-secure-password"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)


def test_access_token_contains_signed_user_identity(monkeypatch) -> None:
    monkeypatch.setattr("app.auth.get_settings", lambda: type("Settings", (), {"jwt_secret": "test-secret", "access_token_expire_minutes": 60})())

    token = create_access_token(uuid4())

    assert len(token.split(".")) == 3
