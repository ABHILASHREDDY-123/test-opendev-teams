from fastapi.testclient import TestClient
from backend.main import app
from backend.models import ContactCreate, ContactOut
import pytest

client = TestClient(app)

token = None

def register_and_login):
 global token
 response = client.post('/auth/register', json={'mobile': '+1234567890', 'password': 'password123'})
 assert response.status_code == 200
 response = client.post('/auth/login', json={'mobile': '+1234567890', 'password': 'password123'})
 assert response.status_code == 200
 token = response.json()['access_token']

@pytest.mark.parametrize('name, mobile', [('John Doe', '+1234567890')])
def test_create_contact(name, mobile):
 register_and_login()
 response = client.post('/contacts/', json={'name': name, 'mobile': mobile}, headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200
 assert response.json()['name'] == name
 assert response.json()['mobile'] == mobile

@pytest.mark.parametrize('name, mobile', [('John Doe', '+1234567890'), ('Jane Doe', '+1234567891')])
def test_list_contacts(name, mobile):
 register_and_login()
 client.post('/contacts/', json={'name': name, 'mobile': mobile}, headers={'Authorization': f'Bearer {token}'})
 client.post('/contacts/', json={'name': 'Jane Doe', 'mobile': '+1234567891'}, headers={'Authorization': f'Bearer {token}'})
 response = client.get('/contacts/', headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200
 assert len(response.json()) == 2

@pytest.mark.parametrize('name, mobile', [('John Doe', '+1234567890')])
def test_update_contact(name, mobile):
 register_and_login()
 client.post('/contacts/', json={'name': name, 'mobile': mobile}, headers={'Authorization': f'Bearer {token}'})
 response = client.put('/contacts/1', json={'name': 'Jane Doe'}, headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200
 assert response.json()['name'] == 'Jane Doe'

@pytest.mark.parametrize('name, mobile', [('John Doe', '+1234567890')])
def test_delete_contact(name, mobile):
 register_and_login()
 client.post('/contacts/', json={'name': name, 'mobile': mobile}, headers={'Authorization': f'Bearer {token}'})
 response = client.delete('/contacts/1', headers={'Authorization': f'Bearer {token}'})
 assert response.status_code == 200