from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_returns_app_info():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "gitlab-cicd-platform"
    assert "version" in body


def test_health_returns_healthy():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_status_returns_running():
    response = client.get("/api/status")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "running"
    assert body["uptime_seconds"] >= 0


def test_users_returns_list():
    response = client.get("/api/users")
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 3
    assert {"id", "name", "email"} <= users[0].keys()


def test_get_single_user():
    response = client.get("/api/users/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_unknown_user_returns_404():
    response = client.get("/api/users/999")
    assert response.status_code == 404
    assert response.json() == {"error": "User 999 not found"}


def test_invalid_user_id_returns_422():
    response = client.get("/api/users/abc")
    assert response.status_code == 422


def test_unknown_route_returns_json_404():
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert "error" in response.json()
