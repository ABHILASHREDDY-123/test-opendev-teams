from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from python_jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

app = FastAPI()

# OAuth2 schema
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

# Password context
pwd_context = CryptContext(schemes=['bcrypt'], default='bcrypt')

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')

# Generate JWT token
def generate_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, 'secret_key', algorithm='HS256')
    return encoded_jwt

# Verify JWT token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, 'secret_key', algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except jwt.JWTClaimsError:
        raise HTTPException(status_code=401, detail='Invalid token')
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail='Invalid token')

# Get current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    email = payload.get('sub')
    # Get user from database
    user = {'email': email}
    return user

# Register user
@app.post('/auth/register', response_model=Token)
async def register_user(email: str, password: str):
    # Hash password
    hashed_password = pwd_context.hash(password)
    # Save user to database
    user = {'email': email, 'password': hashed_password}
    # Generate token
    access_token_expires = timedelta(minutes=30)
    access_token = generate_token(data={'sub': user['email']}, expires_delta=access_token_expires)
    return {'access_token': access_token, 'token_type': 'bearer'}

# Login user
@app.post('/auth/login', response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    # Get user from database
    user = {'email': form_data.username, 'password': 'hashed_password'}
    # Verify password
    if not pwd_context.verify(form_data.password, user['password']):
        raise HTTPException(status_code=401, detail='Invalid email or password')
    # Generate token
    access_token_expires = timedelta(minutes=30)
    access_token = generate_token(data={'sub': user['email']}, expires_delta=access_token_expires)
    return {'access_token': access_token, 'token_type': 'bearer'}
