from fastapi.testclient import TestClient
from main import app
from models import ContactCreate, ContactUpdate
import pytest

def register_and_login(client):
 response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
 assert response.status_code == 201
 response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password'})
 assert response.status_code == 200
 return response.json()['access_token'

def test_create_contact(client):
 access_token = register_and_login(client)
 response = client.post('/contacts', json={'name': 'John Doe', 'mobile': '1234567890'}, headers={'Authorization': f'Bearer {access_token}'})
 assert response.status_code == 201

def test_list_contacts(client):
 access_token = register_and_login(client)
 client.post('/contacts', json={'name': 'John Doe', 'mobile': '1234567890'}, headers={'Authorization': f'Bearer {access_token}'})
 response = client.get('/contacts', headers={'Authorization': f'Bearer {access_token}'})
 assert response.status_code == 200
 assert len(response.json()) == 1

def test_update_contact(client):
 access_token = register_and_login(client)
 response = client.post('/contacts', json={'name': 'John Doe', 'mobile': '1234567890'}, headers={'Authorization': f'Bearer {access_token}'})
 contact_id = response.json()['id']
 response = client.put(f'/contacts/{contact_id}', json={'name': 'Jane Doe'}, headers={'Authorization': f'Bearer {access_token}'})
 assert response.status_code == 200
 assert response.json()['name'] == 'Jane Doe'

def test_delete_contact(client):
 access_token = register_and_login(client)
 response = client.post('/contacts', json={'name': 'John Doe', 'mobile': '1234567890'}, headers={'Authorization': f'Bearer {access_token}'})
 contact_id = response.json()['id']
 response = client.delete(f'/contacts/{contact_id}', headers={'Authorization': f'Bearer {access_token}'})
 assert response.status_code == 200