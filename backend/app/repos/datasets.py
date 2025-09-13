from __future__ import annotations

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.dataset import Dataset


def create(db: Session, session_id: int, name: str, path: str, meta_json: str | None) -> Dataset:
    ds = Dataset(session_id=session_id, name=name, path=path, meta_json=meta_json)
    db.add(ds)
    db.commit()
    db.refresh(ds)
    return ds


def get(db: Session, dataset_id: int) -> Optional[Dataset]:
    return db.query(Dataset).filter(Dataset.id == dataset_id).first()


def latest_for_session(db: Session, session_id: int) -> Optional[Dataset]:
    return db.query(Dataset).filter(Dataset.session_id == session_id).order_by(desc(Dataset.created_at)).first()


def list_for_session(db: Session, session_id: int) -> list[Dataset]:
    return db.query(Dataset).filter(Dataset.session_id == session_id).order_by(desc(Dataset.created_at)).all()


def update_name(db: Session, dataset_id: int, name: str) -> Dataset:
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise ValueError("Dataset not found")
    # Check duplicate name in the same session
    dup = (
        db.query(Dataset)
        .filter(Dataset.session_id == ds.session_id, Dataset.name == name, Dataset.id != dataset_id)
        .first()
    )
    if dup:
        raise ValueError("Duplicate name")
    ds.name = name
    db.add(ds)
    db.commit()
    db.refresh(ds)
    return ds


def exists_name(db: Session, session_id: int, name: str, exclude_id: Optional[int] = None) -> bool:
    q = db.query(Dataset).filter(Dataset.session_id == session_id, Dataset.name == name)
    if exclude_id is not None:
        q = q.filter(Dataset.id != exclude_id)
    return db.query(q.exists()).scalar()  # type: ignore
