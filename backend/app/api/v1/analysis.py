from __future__ import annotations

import json
from fastapi import APIRouter, HTTPException, Depends
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from ...schemas.analysis import (
    TimeSeriesRequest,
    TimeSeriesResponse,
    TimeSeriesSeries,
    TimeSeriesStatistics,
    ParetoRequest,
    ParetoResponse,
    ParetoItem,
    ParetoItemMetadata,
    HistogramRequest,
    HistogramResponse,
    HistogramFit,
)
from ...db import get_db
from ...repos import datasets as datasets_repo
from ...repos import jobs as jobs_repo
from ...utils.dataframe import detect_date_and_store, display_name_for


router = APIRouter()


def _load_df(path: str) -> pd.DataFrame:
    return pd.read_csv(path) if path.lower().endswith(".csv") else pd.read_excel(path)


@router.post("/timeseries", response_model=TimeSeriesResponse)
def get_timeseries_data(payload: TimeSeriesRequest, db: Session = Depends(get_db)) -> TimeSeriesResponse:
    ds = datasets_repo.get(db, payload.dataset_id) if payload.dataset_id else datasets_repo.latest_for_session(db, payload.session_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found for session")

    params = {"store": payload.store, "target_column": payload.target_column, "aggregation": payload.aggregation, "date_range": payload.date_range}
    params_json = json.dumps(params, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    cached = jobs_repo.find_cached(db, payload.session_id, ds.id, "timeseries", params_json)
    if cached:
        return TimeSeriesResponse(**json.loads(cached.result_json))

    df = _load_df(ds.path)
    date_col, store_col = detect_date_and_store(df)
    if date_col is None:
        raise HTTPException(status_code=400, detail="Date column not found")
    if payload.target_column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Target column not found: {payload.target_column}")

    if payload.store and store_col and store_col in df.columns:
        df = df[df[store_col] == payload.store]

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col]).sort_values(date_col)
    if payload.date_range and len(payload.date_range) == 2:
        start, end = payload.date_range
        if start:
            df = df[df[date_col] >= pd.to_datetime(start)]
        if end:
            df = df[df[date_col] <= pd.to_datetime(end)]

    freq = {"daily": "D", "weekly": "W", "monthly": "M"}[payload.aggregation]
    grouped = df.set_index(date_col)[payload.target_column].groupby(pd.Grouper(freq=freq)).sum().dropna()
    values = grouped.values.astype(float)
    timestamps = grouped.index.strftime("%Y-%m-%d").tolist()

    if len(values) > 1:
        mean = float(values.mean()); std = float(values.std(ddof=0)); min_v = float(values.min()); max_v = float(values.max())
        w = min(3, len(values)); start_avg = float(values[:w].mean()); end_avg = float(values[-w:].mean())
        trend = "increasing" if end_avg > start_avg * 1.05 else ("decreasing" if end_avg < start_avg * 0.95 else "flat")
    else:
        mean = std = min_v = max_v = None; trend = "flat"

    stats = TimeSeriesStatistics(mean=mean, std=std, min=min_v, max=max_v, trend=trend)
    resp = TimeSeriesResponse(timestamp=timestamps, series=[TimeSeriesSeries(name=payload.target_column, values=values.tolist(), statistics=stats)], events=[])
    jobs_repo.create(db, payload.session_id, ds.id, "timeseries", params_json, resp.model_dump_json())
    return resp


@router.post("/pareto", response_model=ParetoResponse)
def get_pareto_data(payload: ParetoRequest, db: Session = Depends(get_db)) -> ParetoResponse:
    ds = datasets_repo.get(db, payload.dataset_id) if payload.dataset_id else datasets_repo.latest_for_session(db, payload.session_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found for session")

    params = {"store": payload.store, "analysis_type": payload.analysis_type, "period": payload.period}
    params_json = json.dumps(params, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    cached = jobs_repo.find_cached(db, payload.session_id, ds.id, "pareto", params_json)
    if cached:
        return ParetoResponse(**json.loads(cached.result_json))

    df = _load_df(ds.path)
    date_col, store_col = detect_date_and_store(df)
    if payload.period and date_col and date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=[date_col])
        try:
            period = pd.Period(payload.period)
            df = df[df[date_col].dt.to_period("M") == period]
        except Exception:
            pass
    if payload.store and store_col and store_col in df.columns:
        df = df[df[store_col] == payload.store]

    product_columns = [
        "Mens_JACKETS&OUTER2","Mens_KNIT","Mens_PANTS","WOMEN'S_JACKETS2","WOMEN'S_TOPS","WOMEN'S_ONEPIECE","WOMEN'S_bottoms","WOMEN'S_SCARF & STOLES"
    ]
    present_cols = [c for c in product_columns if c in df.columns]
    if not present_cols:
        raise HTTPException(status_code=400, detail="No product category columns found in data")

    totals = df[present_cols].sum(numeric_only=True)
    pairs = [(col, float(totals[col])) for col in present_cols]
    pairs.sort(key=lambda x: x[1], reverse=True)
    total_sum = sum(v for _, v in pairs) or 0.0

    items: list[ParetoItem] = []
    cumulative = 0.0
    vital_index = (len(pairs) - 1) if pairs else 0
    for i, (cat, val) in enumerate(pairs):
        pct = (val / total_sum * 100.0) if total_sum else 0.0
        cumulative += pct
        if cumulative >= 80.0 and vital_index == (len(pairs) - 1):
            vital_index = i
        items.append(ParetoItem(category=cat, value=val, metadata=ParetoItemMetadata(display_name=display_name_for(cat), percentage=pct, cumulative=cumulative)))
    resp = ParetoResponse(data=items, total=total_sum, vital_few_threshold=vital_index + 1)
    jobs_repo.create(db, payload.session_id, ds.id, "pareto", params_json, resp.model_dump_json())
    return resp


@router.post("/histogram", response_model=HistogramResponse)
def get_histogram_data(payload: HistogramRequest, db: Session = Depends(get_db)) -> HistogramResponse:
    ds = datasets_repo.get(db, payload.dataset_id) if payload.dataset_id else datasets_repo.latest_for_session(db, payload.session_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found for session")

    params = {"column": payload.column, "bins": payload.bins}
    params_json = json.dumps(params, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    cached = jobs_repo.find_cached(db, payload.session_id, ds.id, "histogram", params_json)
    if cached:
        return HistogramResponse(**json.loads(cached.result_json))

    df = _load_df(ds.path)
    if payload.column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column not found: {payload.column}")
    series = pd.to_numeric(df[payload.column], errors="coerce").dropna()
    counts, edges = np.histogram(series.values, bins=payload.bins or 20)
    resp = HistogramResponse(bins=edges.astype(float).tolist(), counts=counts.astype(int).tolist(), fit=HistogramFit(), summary={"count": int(series.shape[0])})
    jobs_repo.create(db, payload.session_id, ds.id, "histogram", params_json, resp.model_dump_json())
    return resp

