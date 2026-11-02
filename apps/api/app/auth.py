import hashlib
from datetime import datetime, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from .db import get_db
from .models import Member, SessionToken

bearer = HTTPBearer(auto_error=False)


def digest(token: str):
    return hashlib.sha256(token.encode()).hexdigest()


def current_member(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)):
    session = db.get(SessionToken, digest(credentials.credentials)) if credentials else None
    if not session or datetime.fromisoformat(session.expires_at) <= datetime.now(timezone.utc):
        raise HTTPException(401, "Sesión ausente o vencida")
    member = db.get(Member, session.member_id)
    if member is None:
        raise HTTPException(401, "Sesión inválida")
    return member


def owner(member: Member = Depends(current_member)):
    if member.role != "owner":
        raise HTTPException(403, "Solo un administrador puede realizar esta acción")
    return member
