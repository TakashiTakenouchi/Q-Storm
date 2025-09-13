from __future__ import annotations

from typing import Optional
from sqlalchemy.orm import Session

from ..models.user import User


def get_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def create(db: Session, username: str, email: str, password_hash: str, full_name: str | None) -> User:
    user = User(username=username, email=email, password_hash=password_hash, full_name=full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

