# backend/app/api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext

from app.db import get_db             # DB セッション依存性
from app.models.user import User      # User モデル（id/username/email/password_hash を想定）

router = APIRouter(
    prefix="/api/v1/users",           # ここで /api/v1/users を付与
    tags=["users"]
)

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------- Pydantic Schemas ----------
class RegisterBody(BaseModel):
    username: str
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    id: int
    username: str
    email: EmailStr


# ---------- Endpoints ----------
@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register_user(body: RegisterBody, db: Session = Depends(get_db)):
    """
    新規ユーザー登録
    - username/email の重複があれば 409
    """
    # 重複チェック
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=409, detail="username already exists")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=409, detail="email already exists")

    try:
        user = User(
            username=body.username,
            email=body.email,
            password_hash=pwd_ctx.hash(body.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="failed to create user")

    return RegisterResponse(id=user.id, username=user.username, email=user.email)


@router.get("/me")
def me_stub():
    """
    /me は最小スタブ（ログイン後に本実装へ差し替え可）
    """
    return {"status": "ok"}
