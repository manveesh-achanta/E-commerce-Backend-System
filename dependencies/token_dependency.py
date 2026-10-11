from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer
import jwt
from jwt import PyJWTError
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
        try:
            decoded_data = jwt.decode(token, key=settings.secret_key.get_secret_value(), algorithms=[settings.algorithm])
        except PyJWTError as jwt_error:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
        return decoded_data

token_bearer = TokenBearer()