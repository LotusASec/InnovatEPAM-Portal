from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, RegisterResponse, TokenResponse
from app.services.auth_service import login_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201, response_model=RegisterResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    user = register_user(db, payload.email, payload.password)
    return RegisterResponse(id=user.id, email=user.email)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    token = login_user(db, payload.email, payload.password)
    return TokenResponse(access_token=token, token_type="bearer")
