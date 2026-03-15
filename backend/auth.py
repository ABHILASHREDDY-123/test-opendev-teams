from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from python_jose import jwt
from datetime import datetime, timedelta

class AuthHandler:
 def __init__(self, secret_key: str):
 self.secret_key = secret_key
 self.pwd_context = CryptContext(schemes=['bcrypt'], default='bcrypt')
 self.access_token_expires = timedelta(minutes=30)

 def get_password_hash(self, password: str):
 return self.pwd_context.hash(password)

 def verify_password(self, plain_password: str, hashed_password: str):
 return self.pwd_context.verify(plain_password, hashed_password)

 def encode_token(self, user_id: int):
 payload = {
 'exp': datetime.utcnow() + self.access_token_expires,
 'iat': datetime.utcnow(),
 'sub': user_id
 }
 return jwt.encode(payload, self.secret_key, algorithm='HS256')

 def decode_token(self, token: str):
 try:
 payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
 return payload['sub']
 except jwt.ExpiredSignatureError:
 raise HTTPException(
 status_code=401,
 detail='Access token expired'
 )
 except jwt.InvalidTokenError:
 raise HTTPException(
 status_code=401,
 detail='Invalid access token'
 )

 def get_current_user(self, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
 token_str = token.credentials
 user_id = self.decode_token(token_str)
 # get user from database using user_id
 # return user
