from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from backend.auth import create_access_token, get_current_user, hash_password, verify_password
from backend.models import ContactCreate, ContactOut, ContactUpdate, TokenResponse, UserLogin, UserOut, UserRegister

class Contact(BaseModel):
    id: int
    name: str
    mobile: str
    owner_id: str

data_store = {
    'users': {},
    'contacts': {}
}

app = FastAPI()

security = HTTPBearer()

@app.post('/auth/register', response_model=UserOut)
async def register(user: UserRegister):
    if user.mobile in data_store['users']:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Mobile number already registered')
    hashed_password = hash_password(user.password)
    user_id = len(data_store['users']) + 1
    data_store['users'][user.mobile] = {'id': user_id, 'password': hashed_password}
    return {'id': user_id, 'mobile': user.mobile}

@app.post('/auth/login', response_model=TokenResponse)
async def login(user: UserLogin):
    if user.mobile not in data_store['users']:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid mobile number or password')
    stored_user = data_store['users'][user.mobile]
    if not verify_password(user.password, stored_user['password']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid mobile number or password')
    access_token = create_access_token({'sub': user.mobile})
    return {'access_token': access_token, 'token_type': 'bearer'}

@app.post('/contacts/', response_model=ContactOut)
async def create_contact(contact: ContactCreate, token: HTTPAuthorizationCredentials = Depends(security)):
    current_user = get_current_user(token.credentials)
    contact_id = len(data_store['contacts']) + 1
    data_store['contacts'][contact_id] = {'id': contact_id, 'name': contact.name, 'mobile': contact.mobile, 'owner_id': current_user['sub']}
    return {'id': contact_id, 'name': contact.name, 'mobile': contact.mobile, 'owner_id': current_user['sub']}

@app.get('/contacts/', response_model=list[ContactOut])
async def read_contacts(token: HTTPAuthorizationCredentials = Depends(security)):
    current_user = get_current_user(token.credentials)
    contacts = [contact for contact in data_store['contacts'].values() if contact['owner_id'] == current_user['sub']]
    return contacts

@app.put('/contacts/{contact_id}', response_model=ContactOut)
async def update_contact(contact_id: int, contact: ContactUpdate, token: HTTPAuthorizationCredentials = Depends(security)):
    current_user = get_current_user(token.credentials)
    if contact_id not in data_store['contacts']:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    stored_contact = data_store['contacts'][contact_id]
    if stored_contact['owner_id'] != current_user['sub']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You do not own this contact')
    if contact.name:
        stored_contact['name'] = contact.name
    if contact.mobile:
        stored_contact['mobile'] = contact.mobile
    return stored_contact

@app.delete('/contacts/{contact_id}')
async def delete_contact(contact_id: int, token: HTTPAuthorizationCredentials = Depends(security)):
    current_user = get_current_user(token.credentials)
    if contact_id not in data_store['contacts']:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    stored_contact = data_store['contacts'][contact_id]
    if stored_contact['owner_id'] != current_user['sub']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You do not own this contact')
    del data_store['contacts'][contact_id]
    return {'message': 'Contact deleted successfully'}