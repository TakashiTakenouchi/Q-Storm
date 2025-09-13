from fastapi import APIRouter, HTTPException, status
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...schemas.user import Token
from ...core.security import verify_password, create_access_token
from ...db import get_db
from ...repos import users as users_repo
from ...repos import sessions as sessions_repo


router = APIRouter()


@router.post("/login", response_model=Token, summary="Obtain access token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = users_repo.get_by_username(db, form_data.username)
    if user is None or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    token = create_access_token(subject=user.username)
    # Create a server-side session row
    from ...core.config import settings
    sess = sessions_repo.create_for_user(db, user_id=user.id, minutes=settings.access_token_expire_minutes)
    return Token(access_token=token, session_id=str(sess.id))

