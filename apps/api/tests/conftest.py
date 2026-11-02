import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db import Base, get_db
from app.main import app, settings
from app.seed import seed


@pytest.fixture
def client(tmp_path):
    url = os.getenv("TEST_DATABASE_URL", "sqlite://")
    if url != "sqlite://" and not (make_url(url).database or "").endswith("_test"):
        raise RuntimeError("TEST_DATABASE_URL debe apuntar a una base dedicada cuyo nombre termine en _test")
    engine = create_engine(url, **({"connect_args": {"check_same_thread": False}, "poolclass": StaticPool} if url == "sqlite://" else {}))
    if url == "sqlite://":
        from sqlalchemy import event

        @event.listens_for(engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine, expire_on_commit=False)
    with factory() as db:
        seed(db)

    def override():
        with factory() as db:
            yield db

    app.dependency_overrides[get_db] = override
    old_dir = settings.upload_dir
    settings.upload_dir = str(tmp_path / "uploads")
    Path(settings.upload_dir).mkdir()
    # Sin context manager para omitir lifespan y no tocar la DB global.
    test_client = TestClient(app)
    yield test_client
    test_client.close()
    app.dependency_overrides.clear()
    settings.upload_dir = old_dir
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def owner_headers(client):
    token = client.post("/api/auth/demo", json={"tenant": "cristal-demo"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_headers(client):
    token = client.post("/api/auth/demo", json={"tenant": "norte-demo"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def viewer_headers(client):
    token = client.post("/api/auth/demo", json={"tenant": "cristal-demo", "role": "viewer"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
