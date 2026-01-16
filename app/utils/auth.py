from jose import jwt, JWTError
from fastapi import Request
from sqlalchemy.orm import Session
from app.models.user import User
from app.security.jwt import SECRET_KEY, ALGORITHM

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
    return user

