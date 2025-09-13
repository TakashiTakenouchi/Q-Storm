Q-Storm Platform — Frontend (React)

Overview
- React + TypeScript app that connects to the FastAPI backend.
- Pages: Login, Data Upload, Analysis (Time Series / Pareto / Histogram).

Prerequisites
- Node.js 18+
- Backend running locally at `http://localhost:8000` (see `backend/README.md`).

Setup
- `cd frontend`
- `npm install`
- `npm run dev` → open the URL shown (usually `http://localhost:5173`)

Dev Proxy
- Vite proxies `/api` to `http://localhost:8000` to avoid CORS during development.

Pages
- Login: obtains JWT via `/api/v1/auth/login` and stores it for subsequent API calls.
- Upload: sends CSV/XLSX to `/api/v1/data/upload`, shows preview and stores `session_id`.
- Analysis: calls `/api/v1/analysis/{timeseries,pareto,histogram}` and renders Plotly charts.

