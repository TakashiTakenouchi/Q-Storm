from __future__ import annotations

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from ..models.session import Session as SessionModel


def create_for_user(db: Session, user_id: int, minutes: int) -> SessionModel:
    now = datetime.now(tz=timezone.utc)
    sess = SessionModel(user_id=user_id, created_at=now, expires_at=now + timedelta(minutes=minutes))
    db.add(sess)
    db.commit()
    db.refresh(sess)
    return sess


def get(db: Session, session_id: int) -> SessionModel | None:
    return db.query(SessionModel).filter(SessionModel.id == session_id).first()

