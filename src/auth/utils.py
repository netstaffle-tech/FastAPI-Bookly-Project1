from fastapi import HTTPException
from datetime import timedelta,datetime
from passlib.context import CryptContext
# pyrefly: ignore [missing-import]
import jwt
from src.config import Config
import uuid
import logging

ACCESS_TOKEN_EXPIRY_TIME = 3600

pass_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def generate_password_hash(password:str)->str:
    return pass_context.hash(password)

def verify_password(password:str,hashed_password:str)->bool:
    return pass_context.verify(password,hashed_password)

def create_access_token(user_data:dict,expiry:timedelta=None,refresh:bool=False):
    payload ={}
    payload['user'] = user_data
    payload['exp'] = datetime.now() + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY_TIME))
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh 
    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM
    )
    return token

def decode_token(token:str)->str:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET_KEY,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=401,detail="Token Expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401,detail="Invalid Token")
    
