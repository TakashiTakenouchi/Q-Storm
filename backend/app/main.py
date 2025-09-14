from pathlib import Path
from fastapi import FastAPI
from .db import Base, engine
from .config import settings
from .routers import health as health_router
from .routers import auth as auth_router
from .routers import datasets as datasets_router
from .routers import analysis as analysis_router
from .repos import users as users_repo
from .db import SessionLocal

app = FastAPI(title="Q-Storm Backend")


@app.on_event("startup")
def on_startup():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # Ensure storage dir exists
    storage_dir = Path(__file__).resolve().parents[2] / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)

    # Optionally seed admin user if password provided
    if settings.DEFAULT_ADMIN_PASSWORD:
        db = SessionLocal()
        try:
            if not users_repo.get_by_username(db, settings.DEFAULT_ADMIN_USERNAME):
                users_repo.create(db, settings.DEFAULT_ADMIN_USERNAME, settings.DEFAULT_ADMIN_PASSWORD)
        finally:
            db.close()


# Routers
app.include_router(health_router.router)
app.include_router(auth_router.router)
app.include_router(datasets_router.router)
app.include_router(analysis_router.router)
