from __future__ import annotations

import io
import json
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import pandas as pd
from sqlalchemy.orm import Session

from ...db import get_db
from ...repos import jobs as jobs_repo


router = APIRouter()


@router.get("/{job_id}")
def export_job(job_id: int, format: str = "csv", db: Session = Depends(get_db)):
    job = jobs_repo.get(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    payload = json.loads(job.result_json)

    if job.type == "timeseries":
        timestamps = payload.get("timestamp", [])
        series = payload.get("series", [])
        name = series[0].get("name", "value") if series else "value"
        values = series[0].get("values", []) if series else []
        df = pd.DataFrame({"timestamp": timestamps, name: values})
    elif job.type == "pareto":
        rows = []
        for item in payload.get("data", []):
            meta = item.get("metadata", {})
            rows.append({
                "category": item.get("category"),
                "value": item.get("value"),
                "percentage": meta.get("percentage"),
                "cumulative": meta.get("cumulative"),
                "display_name": meta.get("display_name"),
            })
        df = pd.DataFrame(rows)
    elif job.type == "histogram":
        bins = payload.get("bins", [])
        counts = payload.get("counts", [])
        rows = []
        for i in range(max(0, len(bins) - 1)):
            rows.append({"bin_start": bins[i], "bin_end": bins[i + 1], "count": counts[i] if i < len(counts) else None})
        df = pd.DataFrame(rows)
    else:
        raise HTTPException(status_code=400, detail="Unsupported job type")

    if format == "csv":
        buf = io.StringIO(); df.to_csv(buf, index=False); buf.seek(0)
        return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=job_{job_id}.csv"})
    elif format == "xlsx":
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        buf.seek(0)
        return StreamingResponse(iter([buf.getvalue()]), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename=job_{job_id}.xlsx"})
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use csv or xlsx")

