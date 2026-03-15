from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def test_create_contact():
 # Register a user
 client.post(
 "/register",
 json={"username": "testuser", "password": "testpassword"}
 )
 # Login to get access token
 response = client.post(
 "/login",
 data={"grant_type": "password", "username": "testuser", "password": "testpassword"}
 )
 access_token = response.json()["access_token"]
 # Create a contact
 response = client.post(
 "/contacts",
 json={"name": "Test Contact", "phone": "1234567890"},
 headers={"Authorization": f"Bearer {access_token}"}
 )
 assert response.status_code == 200
 assert response.json()["message"] == "Contact created successfully"

def test_get_contacts():
 # Register a user
 client.post(
 "/register",
 json={"username": "testuser", "password": "testpassword"}
 )
 # Login to get access token
 response = client.post(
 "/login",
 data={"grant_type": "password", "username": "testuser", "password": "testpassword"}
 )
 access_token = response.json()["access_token"]
 # Get contacts
 response = client.get(
 "/contacts",
 headers={"Authorization": f"Bearer {access_token}"}
 )
 assert response.status_code == 200
 assert len(response.json()) == 0
