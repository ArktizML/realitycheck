from sqlalchemy.orm import Session


def test_authenticate_user(db_session: Session):
    from app.services.auth_service import authenticate_user, create_user
    from app.schemas.user import UserCreate
    user = create_user(db_session, UserCreate(login="a", password="b"))

    authenticated = authenticate_user(db_session, "a", "b")
    assert authenticated is not None
    assert authenticated.id == user.id

    wrong = authenticate_user(db_session, "a", "wrong")
    assert wrong is None
