from pwdlib import PasswordHash
import jwt
from config import settings
from datetime import timedelta, datetime, UTC


hasher = PasswordHash.recommended()


def hash_password(password : str):
    return hasher.hash(password=password)


def verify_password_hash(hash : str, password : str):
    result = hasher.verify(password, hash)
    return result


def create_token(username : str, role : str, id : str, expires : timedelta):
    expire = datetime.now(UTC) + expires
    encode_date = {"username" : username, "role" : role, "id" : id, "exp" : expire}
    token = jwt.encode(encode_date, settings.secret_key.get_secret_value(), algorithm=settings.algorithm)
    return token