from passlib.context import CryptContext
from python_jose import jwt
from datetime import datetime, timedelta
import pytest

crypt_context = CryptContext(schemes=['bcrypt'], default='bcrypt')
secret_key = 'your_secret_key'
algorithm = 'HS256'
access_token_expires_minutes = 30

def hash_password(password: str):
 return crypt_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
 return crypt_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
 expire = datetime.utcnow() + timedelta(minutes=access_token_expires_minutes)
 data.update({'exp': expire})
 return jwt.encode(data, secret_key, algorithm=algorithm)

def get_current_user(token: str):
 try:
 payload = jwt.decode(token, secret_key, algorithms=[algorithm])
 return payload
 except jwt.ExpiredSignatureError:
 return None
 except jwt.InvalidTokenError:
 return None
