# fastapi
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

# 암호화
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta


app = FastAPI()

# Password
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)

# Hashinig
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain,hashed):
    return pwd_context.verify(plain,hashed)

# Access Token ( JWT 형태)
ALGORITHM = "HS256"
SECRET_KEY = "MysteriousSecretKey"      # 환경변수로 !!
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data:dict) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)