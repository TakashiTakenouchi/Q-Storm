from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session
from ..db import get_db
from ..schemas.analysis import AnalysisRequest, AnalysisResponse
from ..repos import analysis as analysis_repo, datasets as datasets_repo

router = APIRouter(tags=["analysis"])

ALLOWED_TYPES = {"timeseries", "pareto", "histogram"}


@router.post("/analysis/{analysis_type}", response_model=AnalysisResponse)
def run_analysis(
    payload: AnalysisRequest,
    analysis_type: str = Path(..., description="timeseries | pareto | histogram"),
    db: Session = Depends(get_db),
):
    atype = analysis_type.lower()
    if atype not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid analysis type",
        )

    ds = datasets_repo.get(db, payload.dataset_id)
    if not ds:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    # Caching stub: use a simple cache key for now
    cache_key = "v1"
    _, created = analysis_repo.get_or_create_job(db, dataset_id=ds.id, job_type=atype, cache_key=cache_key)
    return AnalysisResponse(status="queued", cached=not created)


@router.post("/datasets/{dataset_id}/analysis/{analysis_type}", response_model=AnalysisResponse)
def run_analysis_by_dataset(
    dataset_id: int,
    analysis_type: str = Path(..., description="timeseries | pareto | histogram"),
    db: Session = Depends(get_db),
):
    atype = analysis_type.lower()
    if atype not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid analysis type",
        )

    ds = datasets_repo.get(db, dataset_id)
    if not ds:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    cache_key = "v1"
    _, created = analysis_repo.get_or_create_job(db, dataset_id=ds.id, job_type=atype, cache_key=cache_key)
    return AnalysisResponse(status="queued", cached=not created)
