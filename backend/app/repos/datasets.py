from sqlalchemy.orm import Session
from ..models.dataset import Dataset


def create(db: Session, *, filename: str, path: str, content_type: str, size: int) -> Dataset:
    ds = Dataset(
        filename=filename,
        path=path,
        content_type=content_type,
        size=size,
    )
    db.add(ds)
    db.commit()
    db.refresh(ds)
    return ds


def get(db: Session, dataset_id: int) -> Dataset | None:
    return db.query(Dataset).filter(Dataset.id == dataset_id).first()


def list_all(db: Session) -> list[Dataset]:
    return db.query(Dataset).order_by(Dataset.uploaded_at.desc()).all()
