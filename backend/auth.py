from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional

class Auth:
 def __init__(self, secret_key: str, algorithm: str, access_token_expire_minutes: int):
 self.secret_key = secret_key
 self.algorithm = algorithm
 self.access_token_expire_minutes = access_token_expire_minutes

 def hash_password(self, password: str):
 pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")
 return pwd_context.hash(password)

 def verify_password(self, plain_password: str, hashed_password: str):
 pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")
 return pwd_context.verify(plain_password, hashed_password)

 def create_access_token(self, data: dict):
 access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
 return jwt.encode({
 **data,
 "exp": datetime.utcnow() + access_token_expires
 }, self.secret_key, algorithm=self.algorithm)

 def get_current_user(self, token: str):
 try:
 payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
 username: str = payload.get("sub")
 if username is None:
 raise JWTError
 return username
 except JWTError:
 return None
