from __future__ import annotations

from typing import Optional
from sqlalchemy.orm import Session

from ..models.analysis_job import AnalysisJob


def find_cached(db: Session, session_id: int, dataset_id: int, type_: str, params_json: str) -> Optional[AnalysisJob]:
    return (
        db.query(AnalysisJob)
        .filter(
            AnalysisJob.session_id == session_id,
            AnalysisJob.dataset_id == dataset_id,
            AnalysisJob.type == type_,
            AnalysisJob.params_json == params_json,
        )
        .order_by(AnalysisJob.created_at.desc())
        .first()
    )


def create(db: Session, session_id: int, dataset_id: int, type_: str, params_json: str, result_json: str) -> AnalysisJob:
    job = AnalysisJob(session_id=session_id, dataset_id=dataset_id, type=type_, params_json=params_json, result_json=result_json)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get(db: Session, job_id: int) -> Optional[AnalysisJob]:
    return db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()

