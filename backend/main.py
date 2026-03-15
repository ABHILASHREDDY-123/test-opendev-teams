from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

app = FastAPI()

# OAuth2 schema
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")

# JWT secret key
SECRET_KEY = "secretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# In-memory user storage
users_db = {}

# In-memory contact storage
contacts_db = {}

class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: bool = False

class UserInDB(User):
    password: str

class Contact(BaseModel):
    id: int
    name: str
    email: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(users_db, token_data.username)
    if user is None:
        raise credentials_exception
    return user

class TokenData(BaseModel):
    username: str | None = None

@app.post("/auth/register")
async def register(username: str, password: str):
    if username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = get_password_hash(password)
    users_db[username] = {
        "username": username,
        "email": "",
        "full_name": "",
        "disabled": False,
        "password": hashed_password,
    }
    return {"message": "User created successfully"}

@app.post("/auth/login")
async def login(username: str, password: str):
    user = authenticate_user(users_db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/contacts")
async def create_contact(name: str, email: str, current_user: User = Depends(get_current_user)):
    contact_id = len(contacts_db) + 1
    contacts_db[contact_id] = {
        "id": contact_id,
        "name": name,
        "email": email,
        "owner": current_user.username,
    }
    return {"message": "Contact created successfully"}

@app.get("/contacts")
async def read_contacts(current_user: User = Depends(get_current_user)):
    contacts = [contact for contact in contacts_db.values() if contact["owner"] == current_user.username]
    return contacts

@app.put("/contacts/{contact_id}")
async def update_contact(contact_id: int, name: str, email: str, current_user: User = Depends(get_current_user)):
    if contact_id not in contacts_db:
        raise HTTPException(status_code=404, detail="Contact not found")
    if contacts_db[contact_id]["owner"] != current_user.username:
        raise HTTPException(status_code=403, detail="You do not own this contact")
    contacts_db[contact_id]["name"] = name
    contacts_db[contact_id]["email"] = email
    return {"message": "Contact updated successfully"}

@app.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: int, current_user: User = Depends(get_current_user)):
    if contact_id not in contacts_db:
        raise HTTPException(status_code=404, detail="Contact not found")
    if contacts_db[contact_id]["owner"] != current_user.username:
        raise HTTPException(status_code=403, detail="You do not own this contact")
    del contacts_db[contact_id]
    return {"message": "Contact deleted successfully"}