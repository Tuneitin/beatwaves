import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestAuth:
    def test_register_success(self):
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
                "artist_name": "Test Artist",
                "location": "Ghana",
            },
        )
        assert response.status_code == 201
        assert "access_token" in response.json()
        assert response.json()["user"]["email"] == "test@example.com"

    def test_register_duplicate_email(self):
        client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
                "artist_name": "Test Artist",
            },
        )
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
                "artist_name": "Another Artist",
            },
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_login_success(self):
        client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
                "artist_name": "Test Artist",
            },
        )
        response = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_invalid_password(self):
        client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
                "artist_name": "Test Artist",
            },
        )
        response = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401


class TestTracks:
    @pytest.fixture
    def auth_token(self):
        response = client.post(
            "/auth/register",
            json={
                "email": "artist@example.com",
                "password": "password123",
                "artist_name": "Test Artist",
            },
        )
        return response.json()["access_token"]

    def test_list_tracks_empty(self, auth_token):
        response = client.get(
            "/tracks/",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_list_tracks_requires_auth(self):
        response = client.get("/tracks/")
        assert response.status_code == 403


class TestPayments:
    @pytest.fixture
    def auth_token(self):
        response = client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "password123",
                "artist_name": "Test User",
            },
        )
        return response.json()["access_token"]

    def test_subscribe_starter_free(self, auth_token):
        response = client.post(
            "/payments/subscribe/starter",
            json={
                "amount_ghs": 0,
                "momo_number": "+233551234567",
                "momo_network": "mtn",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
        assert response.json()["amount_ghs"] == 0.0

    def test_get_transaction_status(self, auth_token):
        # First create a transaction
        client.post(
            "/payments/subscribe/starter",
            json={
                "amount_ghs": 0,
                "momo_number": "+233551234567",
                "momo_network": "mtn",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        
        # Try to get status
        response = client.get(
            "/payments/status/nonexistent",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 404


class TestHealth:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
