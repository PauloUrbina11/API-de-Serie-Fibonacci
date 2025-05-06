import pytest
from fastapi.testclient import TestClient
from fibonacci import app, Base, engine, SessionLocal
from sqlalchemy.orm import Session
from datetime import datetime
import base64

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def get_auth_header(username="admin", password="1234"):
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}

def test_generar_fibonacci_manual():
    response = client.post(
        "/fibonacci/manual",
        json={"time": "12:34:45"},
        headers=get_auth_header()
    )
    assert response.status_code == 200
    data = response.json()
    assert data["modo"] == "manual"
    assert data["hora"] == "12:34:45"
    assert len(data["serie"]) == 45 + 2

def test_generar_fibonacci_manual_pruebas(monkeypatch):
    async def mock_send_email(recipient, subject, content):
        return True

    from fibonacci import send_email
    monkeypatch.setattr("fibonacci.send_email", mock_send_email)

    response = client.post(
        "/fibonacci/manual/pruebas",
        json={
            "time": "10:10:10",
            "email": "test@example.com",
            "subject": "Prueba Técnica"
        },
        headers=get_auth_header()
    )
    assert response.status_code == 200
    assert response.json()["modo"] == "manual+correo"

def test_generar_fibonacci_auto():
    response = client.post("/fibonacci/auto", headers=get_auth_header())
    assert response.status_code == 200
    assert response.json()["modo"] == "automático"

def test_generar_fibonacci_auto_y_enviar(monkeypatch):
    async def mock_send_email(recipient, subject, content):
        return True

    monkeypatch.setattr("fibonacci.send_email", mock_send_email)

    response = client.post(
        "/fibonacci/auto/send",
        json={
            "email": "test@example.com",
            "subject": "Envio Automático"
        },
        headers=get_auth_header()
    )
    assert response.status_code == 200
    assert response.json()["modo"] == "automático+correo"

def test_obtener_series():
    response = client.get("/series", headers=get_auth_header())
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_auth_falla():
    response = client.post("/fibonacci/auto", headers=get_auth_header("wrong", "user"))
    assert response.status_code == 401
