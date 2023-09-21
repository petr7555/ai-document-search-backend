from fastapi.testclient import TestClient

from ai_document_search_backend.application import app
from ai_document_search_backend.auth import MAX_LOGIN_ATTEMPTS

client = TestClient(app)


def test_invalid_password():
    response = client.post("/auth/token", data={"username": "marius", "password": "1231"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect username or password"}


def test_invalid_username():
    response = client.post("/auth/token", data={"username": "maris", "password": "123"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect username or password"}


def test_valid_authentication():
    response = client.post("/auth/token", data={"username": "marius", "password": "123"})
    assert response.status_code == 200
    assert response.json() == {"access_token": "marius", "token_type": "bearer"}


def test_lockout():
    response = client.post("/auth/token", data={"username": "marius", "password": "123"})
    assert response.status_code == 200
    for i in range(MAX_LOGIN_ATTEMPTS - 1):
        print(i)
        response = client.post("/auth/token", data={"username": "marius", "password": "123q"})
        assert response.status_code == 400
        assert response.json() == {"detail": "Incorrect username or password"}
    response = client.post("/auth/token", data={"username": "marius", "password": "123q"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Failed login attempts exceed limit. Account locked."}
    response = client.post("/auth/token", data={"username": "marius", "password": "123"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Failed login attempts exceed limit. Account locked."}
