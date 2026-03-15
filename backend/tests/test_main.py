from fastapi.testclient import TestClient
from main import app
import pytest
from pydantic import BaseModel
from jwt import encode, decode

class User(BaseModel):
    username: str
    password: str

class Contact(BaseModel):
    name: str
    phone: str

client = TestClient(app)

def test_register():
    user = User(username='test', password='test')
    response = client.post('/register', json=user.dict())
    assert response.status_code == 200
    assert response.json()['message'] == 'User created successfully'

def test_login():
    user = User(username='test', password='test')
    client.post('/register', json=user.dict())
    response = client.post('/login', json=user.dict())
    assert response.status_code == 200
    assert 'token' in response.json()

def test_create_contact():
    user = User(username='test', password='test')
    client.post('/register', json=user.dict())
    login_response = client.post('/login', json=user.dict())
    token = login_response.json()['token']
    contact = Contact(name='test', phone='1234567890')
    response = client.post('/contacts', json=contact.dict(), headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json()['message'] == 'Contact created successfully'

def test_get_contacts():
    user = User(username='test', password='test')
    client.post('/register', json=user.dict())
    login_response = client.post('/login', json=user.dict())
    token = login_response.json()['token']
    contact = Contact(name='test', phone='1234567890')
    client.post('/contacts', json=contact.dict(), headers={'Authorization': f'Bearer {token}'})
    response = client.get('/contacts', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert len(response.json()) == 1
