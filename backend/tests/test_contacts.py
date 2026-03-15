from fastapi.testclient import TestClient
from main import app
from auth import create_access_token
from models import ContactCreate, ContactOut
import pytest

client = TestClient(app)

def test_create_contact):
 access_token = create_access_token({'sub': 'test_user'})
 contact_data = {'name': 'Test Contact', 'email': 'test@example.com', 'phone': '1234567890'}
 response = client.post('/contacts', json=contact_data, headers={'Authorization': f'Bearer {access_token}'})
 assert response.status_code == 200
 assert response.json()['name'] == contact_data['name']

def test_list_contacts):
 access_token = create_access_token({'sub': 'test_user'})
 client.post('/contacts', json={'name': 'Test Contact 1', 'email': 'test1@example.com', 'phone': '1234567890'}, headers={'Authorization': f'Bearer {access_token}'})
 client.post('/contacts', json={'name': 'Test Contact 2', 'email': 'test2@example.com', 'phone': '1234567890'}, headers={'Authorization': f'Bearer {access_token}'})
 response = client.get('/contacts', headers={'Authorization': f'Bearer {access_token}'})
 assert response.status_code == 200
 assert len(response.json()) == 2

def test_update_contact):
 access_token = create_access_token({'sub': 'test_user'})
 client.post('/contacts', json={'name': 'Test Contact', 'email': 'test@example.com', 'phone': '1234567890'}, headers={'Authorization': f'Bearer {access_token}'})
 contact_id = 1
 contact_data = {'name': 'Updated Test Contact', 'email': 'updated_test@example.com', 'phone': '1234567890'}
 response = client.put(f'/contacts/{contact_id}', json=contact_data, headers={'Authorization': f'Bearer {access_token}'})
 assert response.status_code == 200
 assert response.json()['name'] == contact_data['name']

def test_delete_contact):
 access_token = create_access_token({'sub': 'test_user'})
 client.post('/contacts', json={'name': 'Test Contact', 'email': 'test@example.com', 'phone': '1234567890'}, headers={'Authorization': f'Bearer {access_token}'})
 contact_id = 1
 response = client.delete(f'/contacts/{contact_id}', headers={'Authorization': f'Bearer {access_token}'})
 assert response.status_code == 200
 assert response.json()['message'] == 'Contact deleted'
