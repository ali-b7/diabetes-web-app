import pytest

from app import app, db, User


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


def test_index_redirects_to_login_when_not_logged_in(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_register_and_login_flow(client):
    # Register
    resp = client.post(
        "/register",
        data={
            "email": "test@example.com",
            "password": "secret123",
            "confirm": "secret123",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200

    # Check user exists
    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()
        assert user is not None

    # Login
    resp = client.post(
        "/login",
        data={"email": "test@example.com", "password": "secret123"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Dashboard" in resp.data
