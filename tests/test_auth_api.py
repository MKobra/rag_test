from uuid import uuid4

from fastapi.testclient import TestClient

from app.db import initialize_database
from app.main import app


def test_register_login_and_protected_documents_endpoint() -> None:
    initialize_database()
    email = f"test-{uuid4()}@example.com"

    with TestClient(app) as client:
        assert client.get("/api/documents").status_code == 401
        registered = client.post(
            "/api/auth/register",
            json={"email": email, "password": "strong-pass-123", "password_confirm": "strong-pass-123"},
        )
        assert registered.status_code == 201
        token = registered.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        assert client.get("/api/documents", headers=headers).status_code == 200
        logged_in = client.post(
            "/api/auth/login",
            json={"email": email, "password": "strong-pass-123"},
        )

    assert logged_in.status_code == 200
    assert logged_in.json()["token_type"] == "bearer"


def test_registration_rejects_different_password_confirmation() -> None:
    initialize_database()

    with TestClient(app) as client:
        response = client.post(
            "/api/auth/register",
            json={
                "email": f"mismatch-{uuid4()}@example.com",
                "password": "strong-pass-123",
                "password_confirm": "different-pass-123",
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Пароли не совпадают"
