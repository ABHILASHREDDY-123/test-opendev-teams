from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from auth import create_access_token, verify_password, get_password_hash
from contacts import Contact

app = FastAPI()

# OAuth2 schema
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class User(BaseModel):
    username: str
    email: str
    full_name: str
    password: str

# In-memory user database (replace with a real database)
users_db = {}

# In-memory contact database (replace with a real database)
contacts_db = {}

# Create access token
def create_token(data: dict):
    return create_access_token(data)

# Get current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Replace with a real user retrieval mechanism
    for user_id, user in users_db.items():
        if user["token"] == token:
            return user
    raise HTTPException(status_code=401, detail="Invalid token")

# Register user
@app.post("/auth/register")
async def register(user: User):
    # Check if user already exists
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    # Hash password
    user.password = get_password_hash(user.password)
    # Store user in database
    users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "password": user.password,
        "token": create_token({"sub": user.username})
    }
    return {"message": "User created successfully"}

# Login user
@app.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Replace with a real user retrieval mechanism
    user = users_db.get(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    # Verify password
    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid password")
    # Return access token
    return {"access_token": user["token"], "token_type": "bearer"}

# Create contact
@app.post("/contacts")
async def create_contact(contact: Contact, token: str = Depends(oauth2_scheme)):
    # Get current user
    user = get_current_user(token)
    # Store contact in database
    contacts_db[len(contacts_db)] = {
        "name": contact.name,
        "mobile": contact.mobile,
        "owner": user["username"]
    }
    return {"message": "Contact created successfully"}

# Get contacts
@app.get("/contacts")
async def get_contacts(token: str = Depends(oauth2_scheme)):
    # Get current user
    user = get_current_user(token)
    # Filter contacts by owner
    contacts = [contact for contact in contacts_db.values() if contact["owner"] == user["username"]]
    return contacts