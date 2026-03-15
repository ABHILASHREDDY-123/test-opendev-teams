from passlib.context import CryptContext
from python_jose import jwt
from datetime import datetime, timedelta

crypt_context = CryptContext(schemes=['bcrypt'], default='bcrypt')
secret_key = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
algorithm = 'HS256'
access_token_expires_minutes = 60

def hash_password(password: str):
    return crypt_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return crypt_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    if 'exp' not in to_encode:
        expire = datetime.utcnow() + timedelta(minutes=access_token_expires_minutes)
        to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def get_current_user(token: str):
    payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    return payload