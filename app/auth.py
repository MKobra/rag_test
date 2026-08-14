import base64
import binascii
import hashlib
import hmac
import json
import secrets
import time
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings
from app.db import get_connection


bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"pbkdf2_sha256$310000${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = stored.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations)
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def _encode_part(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _decode_part(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_access_token(user_id: UUID) -> str:
    header = _encode_part(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = _encode_part(
        json.dumps(
            {
                "sub": str(user_id),
                "exp": int(time.time()) + get_settings().access_token_expire_minutes * 60,
            },
            separators=(",", ":"),
        ).encode()
    )
    message = f"{header}.{payload}".encode()
    signature = hmac.new(get_settings().jwt_secret.encode(), message, hashlib.sha256).digest()
    return f"{header}.{payload}.{_encode_part(signature)}"


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> UUID:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Требуется вход")
    try:
        header, payload, signature = credentials.credentials.split(".")
        message = f"{header}.{payload}".encode()
        expected = hmac.new(get_settings().jwt_secret.encode(), message, hashlib.sha256).digest()
        if not hmac.compare_digest(_decode_part(signature), expected):
            raise ValueError
        data = json.loads(_decode_part(payload))
        if int(data["exp"]) < int(time.time()):
            raise ValueError
        user_id = UUID(data["sub"])
    except (ValueError, KeyError, TypeError, binascii.Error, json.JSONDecodeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен")

    with get_connection() as connection:
        exists = connection.execute("SELECT EXISTS (SELECT 1 FROM users WHERE id = %s)", (user_id,)).fetchone()[0]
    if not exists:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
    return user_id
