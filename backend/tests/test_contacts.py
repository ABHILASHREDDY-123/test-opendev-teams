from fastapi.testclient import TestClient
from backend.main import app
import pytest

def register_and_login(client):
    register_response = client.post('/auth/register', json={'mobile': '1234567890', 'password': 'password123'})
    assert register_response.status_code == 200
    login_response = client.post('/auth/login', json={'mobile': '1234567890', 'password': 'password123'})
    assert login_response.status_code == 200
    access_token = login_response.json()['access_token'
    return access_token

class TestContacts:
    def test_create_contact(self, client: TestClient):
        access_token = register_and_login(client)
        response = client.post('/contacts/', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {access_token}'})
        assert response.status_code == 201
        assert 'id' in response.json()
        assert 'name' in response.json()
        assert 'mobile' in response.json()
        assert 'owner_id' in response.json()

    def test_list_contacts(self, client: TestClient):
        access_token = register_and_login(client)
        client.post('/contacts/', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {access_token}'})
        client.post('/contacts/', json={'name': 'Jane Doe', 'mobile': '5555555555'}, headers={'Authorization': f'Bearer {access_token}'})
        response = client.get('/contacts/', headers={'Authorization': f'Bearer {access_token}'})
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_update_contact(self, client: TestClient):
        access_token = register_and_login(client)
        response = client.post('/contacts/', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {access_token}'})
        contact_id = response.json()['id'
        response = client.put(f'/contacts/{contact_id}', json={'name': 'Jane Doe'}, headers={'Authorization': f'Bearer {access_token}'})
        assert response.status_code == 200
        assert response.json()['name'] == 'Jane Doe'

    def test_delete_contact(self, client: TestClient):
        access_token = register_and_login(client)
        response = client.post('/contacts/', json={'name': 'John Doe', 'mobile': '9876543210'}, headers={'Authorization': f'Bearer {access_token}'})
        contact_id = response.json()['id'
        response = client.delete(f'/contacts/{contact_id}', headers={'Authorization': f'Bearer {access_token}'})
        assert response.status_code == 200