from core.security import hash_password, verify_password_hash, create_token
from pwdlib import PasswordHash
from datetime import timedelta
import time
import jwt
from config import settings
import pytest

hasher = PasswordHash.recommended()

def test_hash_password():
    password = "Test@123Example"
    password_hash = hash_password(password)
    response = hasher.verify(password, password_hash)
    assert response == True


def test_verify_password_hash():
    password = "Test@123Example"
    password_hash = hash_password(password)
    response = verify_password_hash(password_hash, password)
    assert response == True


def test_verify_password_hash_with_wrong_password():
    password = "Test@123Example"
    wrong_password = "WrongPassword"
    password_hash = hash_password(password)
    response = verify_password_hash(password_hash, wrong_password)
    assert response == False


def test_create_token():
    token = create_token("TestUser", "customer", "TestId_1", timedelta(hours=1))
    decoded_token = jwt.decode(token, settings.secret_key.get_secret_value(), settings.algorithm)
    assert decoded_token["username"] == "TestUser"
    assert decoded_token["role"] == "customer"
    assert decoded_token["id"] == "TestId_1"


def test_create_token_expired():
    token = create_token("TestUser", "customer", "TestId_1", timedelta(milliseconds=1))
    time.sleep(0.02)
    with pytest.raises(jwt.ExpiredSignatureError):
        decoded_token = jwt.decode(token, settings.secret_key.get_secret_value(), [settings.algorithm])


def test_create_token_malformed():
    token = create_token("TestUser", "customer", "TestId_1", timedelta(minutes=5))
    token = token + "1234321"
    with pytest.raises(jwt.PyJWTError):
            decoded_token = jwt.decode(token, settings.secret_key.get_secret_value(), [settings.algorithm])