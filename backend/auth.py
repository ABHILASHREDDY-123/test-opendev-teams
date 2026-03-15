from backend.models import UserRegister, UserLogin
from passlib.context import CryptContext
from python_jose import jwt
import datetime

crypt_context = CryptContext(schemes=['bcrypt'], default='bcrypt')

def hash_password(password: str):
 return crypt_context.hash(password)

def verify_password(plain: str, hashed: str):
 return crypt_context.verify(plain, hashed)

def create_access_token(data: dict):
 expires_delta = datetime.timedelta(minutes=30)
 expire = datetime.datetime.utcnow() + expires_delta
 data.update({'exp': expire})
 encoded_jwt = jwt.encode(data, 'secret_key', algorithm='HS256')
 return encoded_jwt