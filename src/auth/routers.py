from starlette.status import HTTP_400_BAD_REQUEST
from src.auth.dependencies import RefreshTokenBearer
from fastapi import APIRouter,Depends,status
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import UserCreateModel,UserModel,UserLoginModel
from .service import UserService
from src.db.main import get_session
from fastapi.exceptions import HTTPException
from .utils import create_access_token, decode_token,verify_password
from datetime import datetime,timedelta
from fastapi.responses import JSONResponse
from .dependencies import RefreshTokenBearer,AccessTokenBearer,get_current_user,RoleChecker
from src.db.redis_client import add_jti_to_blocklist

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(['admin','user'])

REFRESH_TOKEN_EXPIRY=2

@auth_router.post("/signup", response_model=UserModel,status_code=201)
async def create_user_account(user_data:UserCreateModel,session:AsyncSession=Depends(get_session)):
    email = user_data.email
    user_exists = await user_service.user_exists(email,session)
    if user_exists:
        raise HTTPException(status_code=403,detail="User with email already exists")
    
    new_user = await user_service.create_user(user_data,session)
    return new_user

@auth_router.post("/login",status_code=status.HTTP_200_OK)
async def login_users(login_data:UserLoginModel,session:AsyncSession=Depends(get_session)):
    email = login_data.email
    password = login_data.password
    if not email or not password:
        raise HTTPException(status_code=400,detail="Email and password are required")

    user = await user_service.get_user_by_email(email,session)
    if user is not None:
        password_valid = verify_password(password,user.password_hash)
        if password_valid:
            access_token = create_access_token(user_data={"email":user.email,"uid":str(user.uid),"role":user.role})
            refresh_token = create_access_token(user_data={"email":user.email,"uid":str(user.uid)},refresh=True,expiry=timedelta(days=REFRESH_TOKEN_EXPIRY))

            return JSONResponse(
                content={
                    "message":"Login Successfull",
                    "access_token":access_token,
                    "refresh_token":refresh_token,
                    "user":{
                        "email":user.email,"uid":str(user.uid),"is_verified":user.is_verified
                    }
                }
            )
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Email or Password")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")


@auth_router.get("/refresh_token")
async def get_new_access_token(token_details:dict=Depends(RefreshTokenBearer())):
    expiry_date = token_details['exp'] 
    if datetime.fromtimestamp(expiry_date)>datetime.now():
        new_access_token = create_access_token(user_data=token_details['user'])
        return JSONResponse(content={"access_token":new_access_token})
    
    raise HTTPException(status_code=HTTP_400_BAD_REQUEST,detail="Invalid or Expired Token")

@auth_router.get("/logout")
async def revoke_token_logout(token_details:dict=Depends(AccessTokenBearer())):
    jti = token_details['jti']
    await add_jti_to_blocklist(jti)
    return JSONResponse(content={"message":"Logged out successfully"},status_code=status.HTTP_200_OK)

@auth_router.get("/me")
async def get_current_user(user = Depends(get_current_user),__:bool=Depends(role_checker)):
    return user
