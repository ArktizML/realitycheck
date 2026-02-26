from jose import jwt, JWTError
from fastapi import Request
from sqlalchemy.orm import Session
from app.models.user import User
from app.security.jwt import SECRET_KEY, ALGORITHM
from app.database import SessionLocal
from app.services.milestone_service import get_user_level
from app.models.event import Event

def get_user_for_templates(request: Request, db: Session):
    token = request.cookies.get("access_token")

    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = str(payload.get("sub"))

    except Exception as e:
        return None

    user = db.query(User).filter(User.id == user_id).first()

    done_count = db.query(User).filter(User.id == int(user_id), Event.status == "done").count()
    user_level = get_user_level(done_count)
    user.level = user_level

    return user


def get_current_user_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = str(payload.get("sub"))
        if user_id is None:
            return None
    except JWTError:
        return None

    db = SessionLocal()
    user = db.query(User).filter(User.id == int(user_id)).first()
    db.close()

    return user
