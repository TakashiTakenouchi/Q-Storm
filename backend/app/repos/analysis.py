from sqlalchemy.orm import Session
from ..models.analysis_job import AnalysisJob


def get_or_create_job(db: Session, *, dataset_id: int, job_type: str, cache_key: str) -> tuple[AnalysisJob, bool]:
    job = (
        db.query(AnalysisJob)
        .filter(
            AnalysisJob.dataset_id == dataset_id,
            AnalysisJob.job_type == job_type,
            AnalysisJob.cache_key == cache_key,
        )
        .first()
    )
    created = False
    if not job:
        job = AnalysisJob(dataset_id=dataset_id, job_type=job_type, cache_key=cache_key)
        db.add(job)
        db.commit()
        db.refresh(job)
        created = True
    return job, created
