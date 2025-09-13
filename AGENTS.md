cd "/mnt/c/Projects/Q-Stormα"

cat > AGENTS.md <<'EOF'
# Q-Storm Platform Agent

## Context
This project implements **FastAPI + React + SQLite** for data analysis.  
The focus is on **local development with WSL2** and a **Vite-based frontend**.

## Tech Stack
- Backend: FastAPI, SQLAlchemy, SQLite, pandas, numpy, openpyxl
- Frontend: React, TypeScript, Vite, Axios, Plotly
- Auth: JWT (HS256) with password hashing (passlib[bcrypt])
- Deployment target: Local WSL2 environment (Linux)

## Guidelines
- Always use **SQLite** (no Postgres).
- Passwords must be hashed with **passlib[bcrypt]** (never store plaintext).
- JWT authentication with **HS256**.
- Datasets are uploaded as **CSV/XLSX** and stored under `./backend/storage/`.
- Analysis jobs (**timeseries, pareto, histogram**) must be cached.
- Exports must be available in **CSV and XLSX** formats.
- Error handling: return **422** for invalid requests, **404** for missing dataset/session.
- Config values (DB path, secret key, token expiration) are always read from `.env`.

## Roadmap
1. **Backend persistence** with SQLite + SQLAlchemy  
2. **Frontend dashboard** with login, upload, and analysis visualization  
3. **Export endpoints** for analysis results (CSV/XLSX)  
4. (Optional) **Caching & optimization** of repeated analysis jobs

## Notes
- Development runs on **local CPU (WSL2)**, not GPU or cloud.
- `.env` must contain:
  - `DATABASE_URL=sqlite:///./app.db`   <!-- ドキュメント上の既定値。実運用は /home 直下でも可 -->
  - `SECRET_KEY=...`
  - `ACCESS_TOKEN_EXPIRE_MINUTES=60`
- Follow modular structure: `app/models/`, `app/repos/`, `frontend/src/pages/`, etc.

## File Structure
- backend/
  - app/
    - main.py
    - models/
    - repos/
    - db.py
  - storage/
  - README.md
  - .env.example
- frontend/
  - src/pages/
  - src/api/
  - README.md
EOF
