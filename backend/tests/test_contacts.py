from fastapi.testclient import TestClient
from main import app
from models import ContactCreate, ContactUpdate
import pytest

client = TestClient(app)

def test_create_contact):
 response = client.post(
 "/auth/register",
 json={"username": "testuser", "password": "testpassword"},
 )
 token_response = client.post(
 "/auth/login",
 json={"username": "testuser", "password": "testpassword"},
 )
 token = token_response.json()["access_token"]
 response = client.post(
 "/contacts",
 json={"name": "testcontact", "email": "test@example.com"},
 headers={"Authorization": f"Bearer {token}"},
 )
 assert response.status_code == 200
 assert response.json()["message"] == "Contact created successfully"

def test_list_contacts):
 response = client.post(
 "/auth/register",
 json={"username": "testuser", "password": "testpassword"},
 )
 token_response = client.post(
 "/auth/login",
 json={"username": "testuser", "password": "testpassword"},
 )
 token = token_response.json()["access_token"]
 client.post(
 "/contacts",
 json={"name": "testcontact1", "email": "test1@example.com"},
 headers={"Authorization": f"Bearer {token}"},
 )
 client.post(
 "/contacts",
 json={"name": "testcontact2", "email": "test2@example.com"},
 headers={"Authorization": f"Bearer {token}"},
 )
 response = client.get(
 "/contacts",
 headers={"Authorization": f"Bearer {token}"},
 )
 assert response.status_code == 200
 assert len(response.json()) == 2

def test_update_contact):
 response = client.post(
 "/auth/register",
 json={"username": "testuser", "password": "testpassword"},
 )
 token_response = client.post(
 "/auth/login",
 json={"username": "testuser", "password": "testpassword"},
 )
 token = token_response.json()["access_token"]
 client.post(
 "/contacts",
 json={"name": "testcontact", "email": "test@example.com"},
 headers={"Authorization": f"Bearer {token}"},
 )
 response = client.put(
 "/contacts/1",
 json={"name": "updatedcontact", "email": "updated@example.com"},
 headers={"Authorization": f"Bearer {token}"},
 )
 assert response.status_code == 200
 assert response.json()["message"] == "Contact updated successfully"

def test_delete_contact):
 response = client.post(
 "/auth/register",
 json={"username": "testuser", "password": "testpassword"},
 )
 token_response = client.post(
 "/auth/login",
 json={"username": "testuser", "password": "testpassword"},
 )
 token = token_response.json()["access_token"]
 client.post(
 "/contacts",
 json={"name": "testcontact", "email": "test@example.com"},
 headers={"Authorization": f"Bearer {token}"},
 )
 response = client.delete(
 "/contacts/1",
 headers={"Authorization": f"Bearer {token}"},
 )
 assert response.status_code == 200
 assert response.json()["message"] == "Contact deleted successfully"