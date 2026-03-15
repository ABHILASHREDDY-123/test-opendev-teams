from fastapi.testclient import TestClient
from main import app
from models import ContactCreate, ContactOut
import pytest

client = TestClient(app)

def test_create_contact():
 # Register and login to get access token
 response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 login_response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password123'})
 access_token = login_response.json()['access_token']
 # Create contact
 response = client.post('/contacts/', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {access_token}'})
 assert response.status_code == 200
 assert 'id' in response.json()
 assert 'name' in response.json()
 assert 'mobile' in response.json()

def test_list_contacts():
 # Register and login to get access token
 response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 login_response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password123'})
 access_token = login_response.json()['access_token']
 # Create two contacts
 client.post('/contacts/', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {access_token}'})
 client.post('/contacts/', json={'name': 'Jane Doe', 'mobile': '5555555555'}, headers={'Authorization': f'Bearer {access_token}'})
 # List contacts
 response = client.get('/contacts/', headers={'Authorization': f'Bearer {access_token}'})
 assert response.status_code == 200
 assert len(response.json()) == 2

def test_update_contact():
 # Register and login to get access token
 response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 login_response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password123'})
 access_token = login_response.json()['access_token']
 # Create contact
 create_response = client.post('/contacts/', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {access_token}'})
 contact_id = create_response.json()['id']
 # Update contact
 response = client.put(f'/contacts/{contact_id}', json={'name': 'Jane Doe', 'mobile': '5555555555'}, headers={'Authorization': f'Bearer {access_token}'})
 assert response.status_code == 200
 assert response.json()['name'] == 'Jane Doe'
 assert response.json()['mobile'] == '5555555555'

def test_delete_contact():
 # Register and login to get access token
 response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
 login_response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password123'})
 access_token = login_response.json()['access_token']
 # Create contact
 create_response = client.post('/contacts/', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {access_token}'})
 contact_id = create_response.json()['id']
 # Delete contact
 response = client.delete(f'/contacts/{contact_id}', headers={'Authorization': f'Bearer {access_token}'})
 assert response.status_code == 200
