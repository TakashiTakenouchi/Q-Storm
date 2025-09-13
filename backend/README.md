Q-Storm Platform — Backend (FastAPI)

Overview
- FastAPI application with user management, dataset storage, and analysis APIs.
- JWT-based auth, password hashing, and SQLite persistence with SQLAlchemy.

Run (dev)
- Create venv: `python -m venv .venv && source .venv/bin/activate` (PowerShell: `.venv\\Scripts\\Activate.ps1`)
- Install: `pip install -r requirements.txt`
- Configure env: copy `.env.example` to `.env` and edit as needed
- Start: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- Open docs: `http://localhost:8000/docs`

Environment
- `APP_NAME` (default: Q-Storm Platform API)
- `DATABASE_URL` (default: `sqlite:///./app.db`)
- `SECRET_KEY` (set for production; dev default is auto-generated if not set)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 60)

API
- Health
  - `GET /api/v1/health` — health probe
- Auth & Users
  - `POST /api/v1/auth/login` — OAuth2 password flow; returns JWT and `session_id`
  - `POST /api/v1/users/register` — create user
  - `GET /api/v1/users/me` — current user (auth)
  - `PATCH /api/v1/users/me` — update email/full_name (auth)
  - `POST /api/v1/users/change-password` — change password (auth)
- Data (sessions/datasets)
  - `POST /api/v1/data/upload` — upload CSV/XLSX (form-data: `file`, optional `session_id`, optional `sheet_name`, optional `name`)
    - Saves file under `backend/storage/YYYYMMDD/`
    - Returns `{ session_id, dataset_id, rows, columns, preview }`
  - `GET /api/v1/data/sessions` — list sessions for current user (auth)
  - `GET /api/v1/data/datasets?session_id=...` — list datasets for a session
  - `PATCH /api/v1/data/datasets/{id}` — rename dataset (unique within the session)
- Analysis (cached by session/dataset/params)
  - `POST /api/v1/analysis/timeseries` — aggregates by daily/weekly/monthly
  - `POST /api/v1/analysis/pareto` — category totals, cumulative %, 80% threshold
  - `POST /api/v1/analysis/histogram` — numeric histogram
  - Each request accepts `session_id` and optional `dataset_id` (defaults to latest dataset for the session)
- Export & Admin
  - `GET /api/v1/export/{job_id}?format=csv|xlsx` — export a previous analysis job
  - `GET /api/v1/admin/debug/overview` — counts and latest job summaries

Usage (data load → analysis)
- Upload: `POST /api/v1/data/upload` (form-data: `file`, optional `session_id`, optional `sheet_name`, optional `name`)
- Use returned `session_id`/`dataset_id` in analysis requests.
- Time series: `POST /api/v1/analysis/timeseries` with `{ session_id, dataset_id?, store?, target_column, aggregation, date_range? }`
- Pareto: `POST /api/v1/analysis/pareto` with `{ session_id, dataset_id?, store?, analysis_type:"product_category", period? }`
- Histogram: `POST /api/v1/analysis/histogram` with `{ session_id, dataset_id?, column, bins? }`

Notes
- SQLite persistence via SQLAlchemy. Tables auto-created on startup.
- Uploaded files saved under `backend/storage/YYYYMMDD/`.
- Passwords are hashed with bcrypt; JWT tokens signed with HS256.
- OAuth2 password flow (`tokenUrl=/api/v1/auth/login`).
- Date and store columns are auto-detected (e.g., `Date`/`年月日`, `shop`/`店舗名`).
- Product category display names map to Japanese when available.

Error Behavior (status codes)
- 400 Bad Request: invalid inputs (e.g., missing target column, invalid name)
- 404 Not Found: session/dataset not found
- 409 Conflict: dataset rename/upload with duplicate name in the same session
- Frontend shows localized JP messages for 400/404/409; other statuses fall back to server `detail` or a generic message.

Caching
- Each analysis endpoint caches by `(session_id, dataset_id, type, params_json)` in `analysis_jobs`.
- A repeated call with identical parameters returns the cached result.

Export
- Use the returned `job_id` (from cache write) or inspect via admin/debug to fetch via `/api/v1/export/{job_id}?format=csv|xlsx`.

Examples (Requests/Responses)

Auth & Users
- Login (form)
  - 説明 (JP): ユーザー名とパスワードでログインし、JWTと`session_id`を取得します。
  - Request (x-www-form-urlencoded):
    username=u&password=Password123!
  - Response:
    {
      "access_token": "<jwt>",
      "token_type": "bearer",
      "session_id": "1"
    }

- Register
  - 説明 (JP): 新規ユーザーを作成します。
  - Request JSON:
    {
      "username": "u",
      "email": "u@example.com",
      "password": "Password123!",
      "full_name": "User Name"
    }
  - Response JSON:
    {
      "id": "1",
      "username": "u",
      "email": "u@example.com",
      "full_name": "User Name",
      "is_active": true
    }

- Me (auth)
  - 説明 (JP): 現在のユーザー情報を取得します。
  - Response JSON:
    {
      "id": "1",
      "username": "u",
      "email": "u@example.com",
      "full_name": "User Name",
      "is_active": true
    }

Data (Upload/Sessions/Datasets)
- Upload (form-data)
  - 説明 (JP): データファイルをアップロードしてデータセットを作成します。`name`を指定すると表示名として保存されます（同一セッション内で一意）。
  - Fields: `file` (CSV/XLSX), optional `session_id`, `sheet_name`, `name`
  - Response JSON:
    {
      "session_id": "1",
      "dataset_id": "10",
      "rows": 1234,
      "columns": ["Date", "shop", "Total_Sales", "..."],
      "preview": [ { "Date": "2024-01-01", "shop": "恵比寿", "Total_Sales": 1000 }, "..." ]
    }

- List sessions (auth)
  - 説明 (JP): 自分のセッション一覧を新しい順に返します。
  - Response JSON:
    [
      { "id": 1, "created_at": "2025-09-13T01:23:45+00:00", "expires_at": "2025-09-13T02:23:45+00:00" }
    ]

- List datasets
  - 説明 (JP): セッションに紐づくデータセット一覧を返します。
  - Response JSON:
    [
      { "id": 10, "name": "Sales_2024", "created_at": "2025-09-13T01:24:00+00:00", "path": "backend/storage/20250913/Sales_2024.xlsx" }
    ]

- Rename dataset
  - 説明 (JP): データセット名を変更します。同一セッション内で一意である必要があります。
  - Request JSON: { "name": "Sales_2024_v2" }
  - Response JSON: { "id": 10, "name": "Sales_2024_v2" }
  - 409 Conflict JSON (duplicate): { "detail": "Dataset name already exists in this session" }

Analysis
- Time series
  - 説明 (JP): 日/週/月で集計し、統計量と簡易トレンドを返します。`dataset_id`未指定の場合はセッションの最新データセットを使用します。
  - Request JSON:
    {
      "session_id": 1,
      "dataset_id": 10,
      "store": "恵比寿",
      "target_column": "Total_Sales",
      "aggregation": "monthly",
      "date_range": ["2019-04-30", "2024-12-31"]
    }
  - Response JSON (shape):
    {
      "timestamp": ["2024-01-31", "2024-02-29", "..."],
      "series": [
        {
          "name": "Total_Sales",
          "values": [12345.0, 15678.0, "..."],
          "statistics": { "mean": 14000.5, "std": 1200.3, "min": 9000.0, "max": 17000.0, "trend": "increasing" }
        }
      ],
      "events": []
    }

  - curl:
    curl -s \
      -X POST http://localhost:8000/api/v1/analysis/timeseries \
      -H 'Content-Type: application/json' \
      -d '{
        "session_id": 1,
        "dataset_id": 10,
        "store": "恵比寿",
        "target_column": "Total_Sales",
        "aggregation": "monthly",
        "date_range": ["2019-04-30", "2024-12-31"]
      }'

- Pareto
  - 説明 (JP): カテゴリ別の合計と累積比率を計算し、80%に到達する閾値を返します。
  - Request JSON:
    {
      "session_id": 1,
      "dataset_id": 10,
      "store": "恵比寿",
      "analysis_type": "product_category",
      "period": "2024-01"
    }
  - Response JSON (example):
    {
      "data": [
        { "category": "Mens_JACKETS&OUTER2", "value": 2500000.0, "metadata": { "display_name": "メンズ ジャケット・アウター", "percentage": 35.2, "cumulative": 35.2 } },
        { "category": "WOMEN'S_TOPS", "value": 1800000.0, "metadata": { "display_name": "レディース トップス", "percentage": 25.4, "cumulative": 60.6 } }
      ],
      "total": 7100000.0,
      "vital_few_threshold": 3
    }

  - curl:
    curl -s \
      -X POST http://localhost:8000/api/v1/analysis/pareto \
      -H 'Content-Type: application/json' \
      -d '{
        "session_id": 1,
        "dataset_id": 10,
        "store": "恵比寿",
        "analysis_type": "product_category",
        "period": "2024-01"
      }'

- Histogram
  - 説明 (JP): 指定した数値カラムのヒストグラムを生成します。
  - Request JSON:
    { "session_id": 1, "dataset_id": 10, "column": "Total_Sales", "bins": 20 }
  - Response JSON (example):
    { "bins": [0, 1000, 2000, "..."], "counts": [2, 5, 9, "..."], "fit": null, "summary": { "count": 345 } }
  - curl:
    curl -s \
      -X POST http://localhost:8000/api/v1/analysis/histogram \
      -H 'Content-Type: application/json' \
      -d '{
        "session_id": 1,
        "dataset_id": 10,
        "column": "Total_Sales",
        "bins": 20
      }'

Export & Admin
- Export job
  - Request: `GET /api/v1/export/{job_id}?format=csv|xlsx`
  - Response: file download with appropriate `Content-Type` and `Content-Disposition` headers

- Admin overview
  - Response JSON:
    {
      "users": 1,
      "sessions": 2,
      "datasets": 3,
      "analysis_jobs": 5,
      "latest_jobs": [ { "id": 12, "type": "timeseries", "created_at": "2025-09-13T01:30:00+00:00" } ]
    }

以下の手順で、ユーザー登録からログイン、データセットのアップロード、分析、エクスポートまでの一連の流れを確認できます。

End-to-End Test (via curl)
1) Register user
   - `curl -s -X POST http://localhost:8000/api/v1/users/register -H 'Content-Type: application/json' -d '{"username":"u","email":"u@example.com","password":"Password123!"}'`

2) Login and capture token + session_id
   - `curl -s -X POST http://localhost:8000/api/v1/auth/login -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=u&password=Password123!'`
   - Response: `{ "access_token": "...", "token_type": "bearer", "session_id": "1" }`

3) Upload dataset with a name (replace `data.xlsx`)
   - `curl -s -X POST http://localhost:8000/api/v1/data/upload -H 'Authorization: Bearer <token>' -F 'file=@data.xlsx' -F 'name=Sales_2024'`
   - Response contains `{ session_id, dataset_id }`

4) List datasets for the session
   - `curl -s -G http://localhost:8000/api/v1/data/datasets --data-urlencode 'session_id=<session_id>'`

5) Run time series analysis (uses dataset_id)
   - `curl -s -X POST http://localhost:8000/api/v1/analysis/timeseries -H 'Content-Type: application/json' -d '{"session_id":<sid>,"dataset_id":<did>,"target_column":"Total_Sales","aggregation":"monthly"}'`
   - Re-run the same body to confirm caching (fast response, identical payload)

6) Rename dataset (success)
   - `curl -s -X PATCH http://localhost:8000/api/v1/data/datasets/<did> -H 'Content-Type: application/json' -d '{"name":"Sales_2024_v2"}'`

7) Rename dataset to a duplicate name (expect 409)
   - `curl -i -X PATCH http://localhost:8000/api/v1/data/datasets/<did> -H 'Content-Type: application/json' -d '{"name":"Sales_2024"}'`
   - Status: 409 Conflict; detail: `Dataset name already exists in this session`
8) Export last job to CSV/XLSX
   - Use a `job_id` from a previous analysis (e.g., by capturing server logs or building an admin list endpoint). Example:
   - `curl -s -o out.csv http://localhost:8000/api/v1/export/1?format=csv`

9) Admin/debug overview
   - `curl -s http://localhost:8000/api/v1/admin/debug/overview`

Next Steps
  - curl:
    curl -s \
      -X POST http://localhost:8000/api/v1/analysis/timeseries \
      -H 'Content-Type: application/json' \
      -d '{
        "session_id": 1,
        "dataset_id": 10,
        "store": "恵比寿",
        "target_column": "Total_Sales",
        "aggregation": "monthly",
        "date_range": ["2019-04-30", "2024-12-31"]
      }'
- Add SQLite/SQLAlchemy persistence for users and sessions.
  - curl:
    curl -s \
      -X POST http://localhost:8000/api/v1/analysis/pareto \
      -H 'Content-Type: application/json' \
      -d '{
        "session_id": 1,
        "dataset_id": 10,
        "store": "恵比寿",
        "analysis_type": "product_category",
        "period": "2024-01"
      }'
- Implement caching and export endpoints.
