import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base
from app.database import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


def test_create_and_get_event(client):
    response = client.post(
        "/events/",
        json={
            "title": "DB Event",
            "expectation": 10,
            "reality": 15
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] is not None
    assert data["gap"] == 5

    get_response = client.get(f"/events/{data['id']}")
    assert get_response.status_code == 200

def test_delete_event(client):
    response = client.post(
        "/events/",
        json={
            "title": "To delete",
            "expectation": 5,
            "reality": 10
        }
    )

    event_id = response.json()["id"]

    delete_response = client.delete(f"/events/{event_id}")
    assert delete_response.status_code == 200

    get_response = client.get(f"/events/{event_id}")
    assert get_response.status_code == 404