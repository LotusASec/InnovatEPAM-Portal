from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import APIError
from app.core.security import decode_token
from app.repositories.user_repository import UserRepository

_security = HTTPBearer()
_repo = UserRepository()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except Exception as exc:
        raise APIError("unauthorized", status_code=401) from exc

    user_id = payload.get("sub")
    if not user_id:
        raise APIError("unauthorized", status_code=401)

    user = _repo.get_by_id(db, int(user_id))
    if not user:
        raise APIError("unauthorized", status_code=401)

    return user


def get_current_admin(user=Depends(get_current_user)):
    if not user.is_admin:
        raise APIError("permission denied", status_code=403)
    return user
