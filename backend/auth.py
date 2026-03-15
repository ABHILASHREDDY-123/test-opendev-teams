from passlib.context import CryptContext
from python_jose import jwt

crypt_context = CryptContext(schemes=['bcrypt'], default='bcrypt')
secret_key = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
algorithm = 'HS256'
access_token_expires_minutes = 30

def hash_password(password: str):
 return crypt_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
 return crypt_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
 return jwt.encode(data, secret_key, algorithm=algorithm)

def get_current_user(token: str):
 payload = jwt.decode(token, secret_key, algorithms=[algorithm])
 return payload