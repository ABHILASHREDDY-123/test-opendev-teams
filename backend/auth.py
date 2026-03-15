from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from python_jose import jwt
import datetime

crypt_context = CryptContext(schemes=['bcrypt'], default='bcrypt')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')
secret_key = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
algorithm = 'HS256'
access_token_expire_minutes = 60

def hash_password(password: str):
    return crypt_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return crypt_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def get_current_user(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Access token expired',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except jwt.JWTClaimsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect token claims',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return username