import pytest

from app import app, get_db, init_db


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"

    monkeypatch.setattr("app.DATABASE", str(db_path))

    with app.app_context():
        init_db()

    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key"
    )

    with app.test_client() as client:
        yield client


def test_login_with_invalid_credentials(client):
    response = client.post(
        "/login",
        data={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Invalid" in response.data or b"invalid" in response.data


def test_student_can_login(client):
    response = client.post(
        "/login",
        data={
            "email": "het@student.example",
            "password": "Student123!"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Volunteer" in response.data or b"Dashboard" in response.data


def test_sql_injection_does_not_bypass_login(client):
    response = client.post(
        "/login",
        data={
            "email": "' OR '1'='1",
            "password": "' OR '1'='1"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Invalid" in response.data or b"login" in response.data.lower()
