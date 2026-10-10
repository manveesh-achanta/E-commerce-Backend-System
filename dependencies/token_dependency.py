from fastapi import Request
from fastapi.security import HTTPBearer
import jwt
from config import settings

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error = True):
        super().__init__(auto_error = auto_error)

    async def __call__(self, request: Request):
        creds = await super().__call__(request)
        if creds is None:
            return None
        token = creds.credentials
        data = await self.decode_token(token)
        return data

    async def decode_token(self, token : str):
        decoded_data = jwt.decode(token, key=settings.secret_key.get_secret_value(), algorithms=[settings.algorithm])
        return decoded_data

token_bearer = TokenBearer()