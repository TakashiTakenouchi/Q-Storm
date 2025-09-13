from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .api.v1 import health, auth, users, analysis, data, export, admin
from .core.config import settings
from .db import init_db


def get_application() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0")

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(health.router, prefix="/api/v1/health", tags=["health"]) 
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"]) 
    app.include_router(users.router, prefix="/api/v1/users", tags=["users"]) 
    app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"]) 
    app.include_router(data.router, prefix="/api/v1/data", tags=["data"]) 
    app.include_router(export.router, prefix="/api/v1/export", tags=["export"]) 
    app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"]) 

    # Startup tasks
    @app.on_event("startup")
    def _startup():
        init_db()
        os.makedirs(os.path.join("backend", "storage"), exist_ok=True)

    return app


app = get_application()
