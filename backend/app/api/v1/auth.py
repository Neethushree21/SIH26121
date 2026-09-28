from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, UserResponse, Token
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

router = APIRouter()

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    """Registers a new drilling engineer / field officer account and issues a JWT token."""
    clean_email = payload.email.strip().lower()

    # Check if user already exists
    existing = db.query(User).filter(User.email == clean_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    # Create user
    new_user = User(
        email=clean_email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        role=payload.role.strip(),
        asset_field=payload.asset_field.strip(),
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT
    access_token = create_access_token(data={
        "sub": new_user.id,
        "email": new_user.email,
        "role": new_user.role
    })

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(new_user)
    )

@router.post("/login", response_model=Token)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    """Authenticates user credentials and issues a JWT token."""
    email = payload.email.strip().lower()
    password = payload.password

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is currently inactive. Contact system administrator."
        )

    access_token = create_access_token(data={
        "sub": user.id,
        "email": user.email,
        "role": user.role
    })

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )

@router.post("/login/token", response_model=Token)
def login_oauth2(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 compatible form login endpoint for Swagger UI authorization."""
    email = form_data.username.strip().lower()
    password = form_data.password

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is currently inactive."
        )

    access_token = create_access_token(data={
        "sub": user.id,
        "email": user.email,
        "role": user.role
    })

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Returns the profile of the currently authenticated drilling engineer."""
    return UserResponse.from_orm(current_user)

@router.post("/seed-demo-users")
def seed_demo_users(db: Session = Depends(get_db)):
    """Seeds default Oil India operational accounts if not already present."""
    demo_accounts = [
        {
            "email": "engineer@oilindia.in",
            "password": "OilIndia@2026",
            "full_name": "Er. Jyoti Saikia",
            "role": "Lead Drilling Engineer",
            "asset_field": "Nahorkatiya Field"
        },
        {
            "email": "superintendent@oilindia.in",
            "password": "OilIndia@2026",
            "full_name": "B. K. Goswami",
            "role": "Drilling Superintendent",
            "asset_field": "Assam Shelf Asset"
        },
        {
            "email": "geologist@oilindia.in",
            "password": "OilIndia@2026",
            "full_name": "Dr. Manash Borah",
            "role": "Chief Geologist",
            "asset_field": "Baghjan Asset"
        }
    ]

    created = []
    for acc in demo_accounts:
        existing = db.query(User).filter(User.email == acc["email"]).first()
        if not existing:
            user = User(
                email=acc["email"],
                hashed_password=hash_password(acc["password"]),
                full_name=acc["full_name"],
                role=acc["role"],
                asset_field=acc["asset_field"],
                is_active=True
            )
            db.add(user)
            created.append(acc["email"])
    db.commit()

    return {
        "status": "success",
        "created_demo_users": created,
        "message": "Demo users seeded successfully."
    }
