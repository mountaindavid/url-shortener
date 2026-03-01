import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["BASE_URL"] = "http://testserver/api"
os.environ["JWT_SECRET"] = "test-secret-key-for-testing"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_EXPIRATION"] = "30"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_token(client):
    register_user = client.post("/api/auth/register", json={
        "username": "testuser",
        "password": "testpassword123",
    })
    assert register_user.status_code == 201, f"Fixture setup failed: {register_user.text}"

    response = client.post("/api/auth/token", data={
        "username": "testuser",
        "password": "testpassword123",
    })
    return response.json()["access_token"]
