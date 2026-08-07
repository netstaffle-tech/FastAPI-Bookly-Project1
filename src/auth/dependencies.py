from h11._abnf import status_code
from sqlalchemy.dialects.postgresql import Any
from fastapi import Depends
from fastapi import Request, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from src.auth.utils import decode_token
from fastapi.exceptions import HTTPException
from src.db.redis_client import token_in_blocklist
from src.db.main import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.service import UserService
from typing import List
from .models import User

user_service = UserService()

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        # Extract Bearer token from Authorization header
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        token = credentials.credentials

        # Decode token only once
        token_data = decode_token(token)
        
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or expired",
                    "resolution": "Please get a new token",
                },
            )

        if await token_in_blocklist(token_data['jti']):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail = {
                    "error":"This token is invalid or has been revoked",
                    "resolution":"Please get new token"
                }
            )
        self.verify_token_data(token_data)
        return token_data
    
    def verify_token_data(self,token_data:dict)->None:
        raise NotImplementedError("Please override this method in child classes")

class AccessTokenBearer(TokenBearer):
    def verify_token_data(self,token_data:dict)->None:
         if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an access token",
            )

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self,token_data:dict)->None:
         if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an refresh token",
            )

async def get_current_user(
    token_details:dict = Depends(AccessTokenBearer()),
    session:AsyncSession = Depends(get_session)
    ):
    user_email = token_details['user']['email']
    user = await user_service.get_user_by_email(user_email,session)
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    return user


class RoleChecker:
    def __init__(self,allowed_roles:list[str])->None:
        self.allowed_roles = allowed_roles
    
    def __call__(self,current_user:User=Depends(get_current_user))->Any:
        if current_user.role in self.allowed_roles:
            return True
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not allowed to perform this action.")

