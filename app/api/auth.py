from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import authenticate_user, create_user
from app.security.jwt import create_access_token
from app.schemas.user import UserLogin, UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(
    response: Response,
    data: UserLogin,
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, data.login, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
    )

    return {"message": "Logged in"}

@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    user = create_user(db, user_data)
    return {"id": user.id, "login": user.login}
