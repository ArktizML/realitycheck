from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.security.password import hash_password, verify_password

def create_user(db: Session, user_data: UserCreate) -> User:
    user = User(
        login=user_data.login,
        hashed_password=hash_password(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, login: str, password: str):
    user = db.query(User).filter(User.login == login).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
