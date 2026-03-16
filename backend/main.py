from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from backend.models import UserRegister, UserLogin, UserOut, TokenResponse, ContactCreate, ContactUpdate, ContactOut, generate_uuid
from backend.auth import hash_password, verify_password, create_access_token, get_current_user
from typing import Annotated

app = FastAPI()

# In-memory databases
users_db = {}
contacts_db = {}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')

@app.post('/auth/register', status_code=201, response_model=UserOut)
async def register_user(user: UserRegister):
    if user.mobile in users_db:
        raise HTTPException(status_code=409, detail='Mobile number already registered')
    user_id = generate_uuid()
    hashed_password = hash_password(user.password)
    users_db[user.mobile] = {
        'id': user_id,
        'mobile': user.mobile,
        'hashed_password': hashed_password
    }
    return {'id': user_id, 'mobile': user.mobile}

@app.post('/auth/login', response_model=TokenResponse)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    access_token = create_access_token(data={'sub': user['id'], 'mobile': user['mobile']})
    return {'access_token': access_token, 'token_type': 'bearer'}

async def get_current_active_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail='Not authenticated')
    return user

@app.post('/contacts', status_code=201, response_model=ContactOut)
async def create_contact(
    contact: ContactCreate,
    current_user: Annotated[dict, Depends(get_current_active_user)]
):
    contact_id = generate_uuid()
    new_contact = {
        'id': contact_id,
        'name': contact.name,
        'mobile': contact.mobile,
        'owner_id': current_user['id']
    }
    contacts_db[contact_id] = new_contact
    return new_contact

@app.get('/contacts', response_model=list[ContactOut])
async def read_contacts(current_user: Annotated[dict, Depends(get_current_active_user)]):
    return [
        contact for contact in contacts_db.values()
        if contact['owner_id'] == current_user['id']
    ]

@app.put('/contacts/{contact_id}', response_model=ContactOut)
async def update_contact(
    contact_id: str,
    contact: ContactUpdate,
    current_user: Annotated[dict, Depends(get_current_active_user)]
):
    existing = contacts_db.get(contact_id)
    if not existing or existing['owner_id'] != current_user['id']:
        raise HTTPException(status_code=404, detail='Contact not found')
    if contact.name is not None:
        existing['name'] = contact.name
    if contact.mobile is not None:
        existing['mobile'] = contact.mobile
    return existing

@app.delete('/contacts/{contact_id}')
async def delete_contact(
    contact_id: str,
    current_user: Annotated[dict, Depends(get_current_active_user)]
):
    contact = contacts_db.get(contact_id)
    if not contact or contact['owner_id'] != current_user['id']:
        raise HTTPException(status_code=404, detail='Contact not found')
    del contacts_db[contact_id]
    return {'message': 'Contact deleted successfully'}