from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.database import get_db
from app.models.userModel import UserModel
from app.schemas.userSchema import UserCreate, UserLogin, UserResponse
from app.schemas.auth import Token
from app.utils.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = (
        db.query(UserModel)
        .filter(
            (UserModel.email == user.email) |
            (UserModel.username == user.username)
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email or username already registered",
        )

    try:
        hashed_password = get_password_hash(user.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    new_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login", response_model=Token)
def login_user(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(UserModel).filter(
        UserModel.email == user.email
    ).first()

    if not db_user or not verify_password(
        user.password,
        db_user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={"sub": str(db_user.id)},
        expires_delta=timedelta(minutes=30),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }