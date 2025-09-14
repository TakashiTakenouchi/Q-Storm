from pathlib import Path
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import get_db
from ..schemas.datasets import DatasetOut
from ..repos import datasets as datasets_repo

router = APIRouter(tags=["datasets"])

ALLOWED_EXTS = {".csv", ".xlsx"}
ALLOWED_CT = {
    "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

# Resolve backend/storage relative to this file
STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/datasets", response_model=DatasetOut, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unsupported file type")
    if file.content_type not in ALLOWED_CT:
        # Some browsers may send 'application/vnd.ms-excel' for CSV; we gate by extension above
        pass

    unique_name = f"{uuid.uuid4().hex}{ext}"
    dest = STORAGE_DIR / unique_name

    # Persist file to storage
    size = 0
    with dest.open("wb") as out:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            out.write(chunk)

    ds = datasets_repo.create(
        db,
        filename=file.filename,
        path=str(dest),
        content_type=file.content_type,
        size=size,
    )
    return ds
