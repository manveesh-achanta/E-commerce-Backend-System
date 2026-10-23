from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from dependencies.token_dependency import token_bearer
from datetime import timedelta
from core.security import create_token
from starlette import status

app = FastAPI()

@app.get("/protected")
async def protected(decoded_data : dict = Depends(token_bearer)):
    return decoded_data


client = TestClient(app)


def test_token_bearer_valid_token():
    token = create_token("TestUser", "customer", "TestId_1", timedelta(hours=1))
    response = client.get("/protected", headers = {"Authorization" : f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "TestUser"


def test_token_bearer_invalid_token():
    response = client.get("/protected", headers = {"Authorization" : f"Bearer Invalid Token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid Token"}


def test_token_bearer_expired_token():
    token = create_token("TestUser", "customer", "TestId_1", timedelta(milliseconds=-1))
    response = client.get("/protected", headers = {"Authorization" : f"Bearer {token}"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail" : "Invalid Token"}


def test_token_bearer_no_token():
    response = client.get("/protected")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}