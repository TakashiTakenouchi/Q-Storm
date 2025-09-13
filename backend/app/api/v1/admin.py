from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...db import get_db
from ...models.user import User
from ...models.session import Session as SessionModel
from ...models.dataset import Dataset
from ...models.analysis_job import AnalysisJob


router = APIRouter()


@router.get("/debug/overview")
def overview(db: Session = Depends(get_db)):
    return {
        "users": db.query(User).count(),
        "sessions": db.query(SessionModel).count(),
        "datasets": db.query(Dataset).count(),
        "analysis_jobs": db.query(AnalysisJob).count(),
        "latest_jobs": [
            {"id": j.id, "type": j.type, "created_at": j.created_at.isoformat()}
            for j in db.query(AnalysisJob).order_by(AnalysisJob.created_at.desc()).limit(10)
        ],
    }

