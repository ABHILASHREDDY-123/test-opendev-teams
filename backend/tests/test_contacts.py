from fastapi.testclient import TestClient
from backend.main import app
from backend.auth import get_current_user
from backend.models import ContactCreate, ContactOut, UserRegister, UserLogin
import pytest

client = TestClient(app)

def test_create_contact():
 # Register a user
 client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 # Login to get the token
 response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password123'})
 token = response.json()['access_token']
 # Create a contact
 response = client.post('/contacts/', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 201
 assert response.json()['name'] == 'John Doe'
 assert response.json()['mobile'] == '9876543210'

def test_list_contacts():
 # Register a user
 client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 # Login to get the token
 response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password123'})
 token = response.json()['access_token']
 # Create two contacts
 client.post('/contacts/', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {token}'})
 client.post('/contacts/', json={'name': 'Jane Doe', 'mobile': '5555555555'}, headers={'Authorization': f'Bearer {token}'})
 # List contacts
 response = client.get('/contacts/', headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200
 assert len(response.json()) == 2

def test_update_contact():
 # Register a user
 client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 # Login to get the token
 response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password123'})
 token = response.json()['access_token']
 # Create a contact
 response = client.post('/contacts/', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {token}'})
 contact_id = response.json()['id']
 # Update the contact
 response = client.put(f'/contacts/{contact_id}', json={'name': 'Jane Doe'}, headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200
 assert response.json()['name'] == 'Jane Doe'

def test_delete_contact():
 # Register a user
 client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 # Login to get the token
 response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password123'})
 token = response.json()['access_token']
 # Create a contact
 response = client.post('/contacts/', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {token}'})
 contact_id = response.json()['id']
 # Delete the contact
 response = client.delete(f'/contacts/{contact_id}', headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200