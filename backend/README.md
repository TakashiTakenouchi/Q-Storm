# Q-Storm Backend (FastAPI)

Requirements are loaded from `.env`. See `.env.example`.

## Endpoints (MVP)
- `GET /health` — service health
- `POST /auth/token` — OAuth2 password flow, returns JWT (HS256)
- `POST /datasets` — upload CSV/XLSX into `./backend/storage/`
- `POST /analysis/{type}` — stub accepting `timeseries|pareto|histogram`

## Run (development)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

## Notes
- SQLite only. Configure with `DATABASE_URL` in `.env`.
- Passwords hashed via `passlib[bcrypt]`; JWT uses HS256.
- Uploads are stored under `./backend/storage/`.
- `.env` must define at least:
  - `DATABASE_URL=sqlite:///./app.db`
  - `SECRET_KEY=...`
  - `ACCESS_TOKEN_EXPIRE_MINUTES=60`
- Optional: `DEFAULT_ADMIN_PASSWORD` to seed `DEFAULT_ADMIN_USERNAME` (default: `admin`).
