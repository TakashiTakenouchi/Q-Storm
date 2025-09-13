from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


Aggregation = Literal["daily", "weekly", "monthly"]


class TimeSeriesStatistics(BaseModel):
    mean: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    trend: Optional[str] = None


class TimeSeriesSeries(BaseModel):
    name: str
    values: List[float]
    statistics: Optional[TimeSeriesStatistics] = None


class TimeSeriesRequest(BaseModel):
    session_id: int
    dataset_id: Optional[int] = None
    store: Optional[str] = None
    target_column: str
    aggregation: Aggregation = "monthly"
    date_range: Optional[List[str]] = Field(default=None, description="[start, end] as YYYY-MM-DD")


class TimeSeriesResponse(BaseModel):
    timestamp: List[str]
    series: List[TimeSeriesSeries]
    events: Optional[List[dict]] = None


class ParetoItemMetadata(BaseModel):
    display_name: Optional[str] = None
    percentage: Optional[float] = None
    cumulative: Optional[float] = None


class ParetoItem(BaseModel):
    category: str
    value: float
    metadata: ParetoItemMetadata = ParetoItemMetadata()


class ParetoRequest(BaseModel):
    session_id: int
    dataset_id: Optional[int] = None
    store: Optional[str] = None
    analysis_type: Literal["product_category"] = "product_category"
    period: Optional[str] = None


class ParetoResponse(BaseModel):
    data: List[ParetoItem]
    total: float
    vital_few_threshold: int


class HistogramRequest(BaseModel):
    session_id: int
    dataset_id: Optional[int] = None
    column: str
    bins: Optional[int] = 20


class HistogramFit(BaseModel):
    distribution: Optional[str] = None
    params: Optional[dict] = None


class HistogramResponse(BaseModel):
    bins: List[float]
    counts: List[int]
    fit: Optional[HistogramFit] = None
    summary: Optional[dict] = None

