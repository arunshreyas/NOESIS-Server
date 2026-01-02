import os
from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated="auto",
)


def get_password_hash(password: str) -> str:
    if len(password.encode("utf-8")) > 4096:
        raise ValueError("Password too long (max 4096 bytes)")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})

    secret_key = os.getenv("SECRET_KEY", "change-me")
    algorithm = os.getenv("ALGORITHM", "HS256")

    return jwt.encode(to_encode, secret_key, algorithm=algorithm)
