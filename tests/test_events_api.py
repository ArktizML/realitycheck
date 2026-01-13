from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_event_endpoint():
    response = client.post("api/events", json={
        "title": "API Event",
        "expectation": 10,
        "reality": 20
    })

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "API Event"
    assert data["expectation"] == 10
    assert data["reality"] == 20
    assert data["gap"] == 10
    assert "id" in data