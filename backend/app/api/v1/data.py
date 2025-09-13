from __future__ import annotations

from typing import Optional
import io
import json
import os
from datetime import datetime

import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Depends
from sqlalchemy.orm import Session

from ...db import get_db
from ...repos import sessions as sessions_repo
from ...repos import datasets as datasets_repo


router = APIRouter()


@router.post("/upload", summary="Upload a CSV/XLSX file and create/update session")
async def upload_data(
    file: UploadFile = File(...),
    session_id: Optional[int] = Form(default=None),
    sheet_name: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
):
    try:
        filename = file.filename or "uploaded"
        content = await file.read()
        if filename.lower().endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        elif filename.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name or 0)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use CSV or Excel.")

        # Ensure session record exists; if not provided, create anonymous session (user_id=0)
        if session_id:
            sess = sessions_repo.get(db, session_id)
            if not sess:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            from ...core.config import settings  # to get expiry minutes
            sess = sessions_repo.create_for_user(db, user_id=0, minutes=settings.access_token_expire_minutes)

        # Save file to storage path
        base_dir = os.path.join("backend", "storage", datetime.now().strftime("%Y%m%d"))
        os.makedirs(base_dir, exist_ok=True)
        ext = ".csv" if filename.lower().endswith(".csv") else ".xlsx"
        safe_name = os.path.splitext(os.path.basename(filename))[0]
        unique = datetime.now().strftime("%H%M%S%f")
        stored_name = f"{safe_name}_{unique}{ext}"
        abs_path = os.path.join(base_dir, stored_name)
        with open(abs_path, "wb") as f:
            f.write(content)

        meta = {
            "original_name": filename,
            "sheet_name": sheet_name,
            "columns": list(map(str, df.columns.tolist())),
        }
        ds = datasets_repo.create(db, session_id=sess.id, name=filename, path=abs_path, meta_json=json.dumps(meta, ensure_ascii=False))

        return {
            "session_id": str(sess.id),
            "dataset_id": str(ds.id),
            "rows": int(len(df)),
            "columns": meta["columns"],
            "preview": df.head(5).to_dict(orient="records"),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

