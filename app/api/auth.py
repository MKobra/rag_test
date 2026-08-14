from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.auth import create_access_token, hash_password, verify_password
from app.db import get_connection
from app.schemas.auth import AuthRequest, AuthResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _auth_response(user_id, email: str) -> AuthResponse:
    return AuthResponse(access_token=create_access_token(user_id), user_id=user_id, email=email)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(request: AuthRequest) -> AuthResponse:
    if request.password_confirm != request.password:
        raise HTTPException(status_code=400, detail="Пароли не совпадают")
    email = request.email.lower()
    user_id = uuid4()
    try:
        with get_connection() as connection:
            connection.execute(
                "INSERT INTO users (id, email, password_hash) VALUES (%s, %s, %s)",
                (user_id, email, hash_password(request.password)),
            )
            connection.commit()
    except Exception as error:
        if "unique" in str(error).lower():
            raise HTTPException(status_code=409, detail="Пользователь уже зарегистрирован") from error
        raise
    return _auth_response(user_id, email)


@router.post("/login", response_model=AuthResponse)
def login(request: AuthRequest) -> AuthResponse:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, email, password_hash FROM users WHERE email = %s",
            (request.email.lower(),),
        ).fetchone()
    if not row or not verify_password(request.password, row[2]):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    return _auth_response(row[0], row[1])
