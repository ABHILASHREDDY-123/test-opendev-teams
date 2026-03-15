from fastapi.testclient import TestClient
from backend.main import app
from backend.models import ContactCreate, ContactUpdate
import pytest

client = TestClient(app)

def register_and_login():
 register_response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
 login_response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password'})
 return login_response.json()['access_token'
]

def test_create_contact():
 token = register_and_login()
 response = client.post('/contacts/', json={'name': 'John Doe', 'mobile': '1234567890'}, headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 201
 assert response.json()['name'] == 'John Doe'

def test_list_contacts():
 token = register_and_login()
 client.post('/contacts/', json={'name': 'John Doe', 'mobile': '1234567890'}, headers={'Authorization': f'Bearer {token}'})
 client.post('/contacts/', json={'name': 'Jane Doe', 'mobile': '1234567891'}, headers={'Authorization': f'Bearer {token}'})
 response = client.get('/contacts/', headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200
 assert len(response.json()) == 2

def test_update_contact():
 token = register_and_login()
 client.post('/contacts/', json={'name': 'John Doe', 'mobile': '1234567890'}, headers={'Authorization': f'Bearer {token}'})
 response = client.put('/contacts/1', json={'name': 'Jane Doe'}, headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200
 assert response.json()['name'] == 'Jane Doe'

def test_delete_contact():
 token = register_and_login()
 client.post('/contacts/', json={'name': 'John Doe', 'mobile': '1234567890'}, headers={'Authorization': f'Bearer {token}'})
 response = client.delete('/contacts/1', headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200