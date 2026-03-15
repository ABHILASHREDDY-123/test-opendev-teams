from fastapi.testclient import TestClient
from backend.main import app
import pytest

client = TestClient(app)

def test_register():
 response = client.post('/register', json={'username': 'test', 'password': 'test'})
 assert response.status_code == 200
 assert response.json()['message'] == 'User created successfully'

def test_login():
 client.post('/register', json={'username': 'test', 'password': 'test'})
 response = client.post('/login', json={'username': 'test', 'password': 'test'})
 assert response.status_code == 200
 assert 'token' in response.json()

def test_create_contact():
 client.post('/register', json={'username': 'test', 'password': 'test'})
 login_response = client.post('/login', json={'username': 'test', 'password': 'test'})
 token = login_response.json()['token']
 response = client.post('/contacts', json={'name': 'test', 'phone': '123'}, headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200
 assert response.json()['message'] == 'Contact created successfully'

def test_get_contacts():
 client.post('/register', json={'username': 'test', 'password': 'test'})
 login_response = client.post('/login', json={'username': 'test', 'password': 'test'})
 token = login_response.json()['token']
 response = client.get('/contacts', headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200
 assert 'contacts' in response.json()

def test_update_contact():
 client.post('/register', json={'username': 'test', 'password': 'test'})
 login_response = client.post('/login', json={'username': 'test', 'password': 'test'})
 token = login_response.json()['token']
 client.post('/contacts', json={'name': 'test', 'phone': '123'}, headers={'Authorization': f'Bearer {token}'})
 response = client.put('/contacts/test', json={'name': 'test', 'phone': '456'}, headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200
 assert response.json()['message'] == 'Contact updated successfully'

def test_delete_contact():
 client.post('/register', json={'username': 'test', 'password': 'test'})
 login_response = client.post('/login', json={'username': 'test', 'password': 'test'})
 token = login_response.json()['token']
 client.post('/contacts', json={'name': 'test', 'phone': '123'}, headers={'Authorization': f'Bearer {token}'})
 response = client.delete('/contacts/test', headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200
 assert response.json()['message'] == 'Contact deleted successfully'
