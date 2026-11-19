from datetime import datetime, timedelta
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash


from dotenv import load_dotenv
import os
load_dotenv()

secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")
access_token_expire_minutes = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

# Password hashing
password_hash = PasswordHash.recommended()

# change to jwt
security=HTTPBearer()

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def get_current_user(token: HTTPAuthorizationCredentials=Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, secret_key, algorithms=[algorithm])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception

        return True
    except InvalidTokenError:
        raise credentials_exception
    

