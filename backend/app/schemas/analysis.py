from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    dataset_id: int = Field(..., ge=1)


class AnalysisResponse(BaseModel):
    status: str
    cached: bool = False
