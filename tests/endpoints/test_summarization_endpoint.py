import pytest

from fastapi.testclient import TestClient

from ai_document_search_backend.application import app

test_username = "test_user"
test_password = "test_password"

app.container.config.auth.secret_key.from_value("test_secret_key")
app.container.config.auth.username.from_value(test_username)
app.container.config.auth.password.from_value(test_password)

client = TestClient(app)


@pytest.fixture
def get_token():
    response = client.post(
        "/auth/token", data={"username": test_username, "password": test_password}
    )
    return response.json()["access_token"]


def test_not_authenticated():
    response = client.get("/summarization")
    assert response.status_code == 401


def test_summarize_text(get_token):
    response = client.get(
        "/summarization?text=Hello%20World&summary_length=5",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200
    assert response.json() == {"summary": "Hello"}


def test_missing_text_parameter(get_token):
    response = client.get("/summarization", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": None,
                "loc": ["query", "text"],
                "msg": "Field required",
                "type": "missing",
                "url": "https://errors.pydantic.dev/2.4/v/missing",
            }
        ]
    }


def test_default_summary_length(get_token):
    response = client.get(
        "/summarization?text=Hello%20World",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200
    assert response.json() == {"summary": "Hello Worl"}
