from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env.test", override=True)

import pytest # noqa: E402
from fastapi.testclient import TestClient # noqa: E402

from app.main import app # noqa: E402
from app.core.db import Base, engine # noqa: E402

from app.core.db import SessionLocal # noqa: E402
from app.models.user import User # noqa: E402


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def get_token(client):
    def _get_token(email: str, name: str, password: str) -> str:
        register_response = client.post(
            "/auth/register",
            json={
                "email": email,
                "name": name,
                "password": password,
            },
        )
        assert register_response.status_code == 200

        login_response = client.post(
            "/auth/login",
            data={
                "username": email,
                "password": password,
            },
        )
        assert login_response.status_code == 200

        return login_response.json()["access_token"]

    return _get_token


@pytest.fixture
def make_admin():
    def _make_admin(email: str):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            user.role = "admin"
            db.commit()
        finally:
            db.close()

    return _make_admin