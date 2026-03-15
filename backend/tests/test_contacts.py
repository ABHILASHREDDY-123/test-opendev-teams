from fastapi.testclient import TestClient
from backend.main import app
from backend.models import ContactCreate, ContactOut
import pytest

client = TestClient(app)

def test_create_contact():
 response = client.post("/auth/register", json={"mobile": "1234567890", "password": "password123"})
 access_token = response.json()["access_token"]
 response = client.post("/contacts", json={"name": "John Doe", "mobile": "1234567890"}, headers={"Authorization": "Bearer " + access_token})
 assert response.status_code == 201
 assert response.json()["name"] == "John Doe"

def test_list_contacts():
 response = client.post("/auth/register", json={"mobile": "1234567890", "password": "password123"})
 access_token = response.json()["access_token"]
 client.post("/contacts", json={"name": "John Doe", "mobile": "1234567890"}, headers={"Authorization": "Bearer " + access_token})
 client.post("/contacts", json={"name": "Jane Doe", "mobile": "1234567891"}, headers={"Authorization": "Bearer " + access_token})
 response = client.get("/contacts", headers={"Authorization": "Bearer " + access_token})
 assert response.status_code == 200
 assert len(response.json()) == 2

def test_update_contact():
 response = client.post("/auth/register", json={"mobile": "1234567890", "password": "password123"})
 access_token = response.json()["access_token"]
 response = client.post("/contacts", json={"name": "John Doe", "mobile": "1234567890"}, headers={"Authorization": "Bearer " + access_token})
 contact_id = response.json()["id"]
 response = client.put(f"/contacts/{contact_id}", json={"name": "Jane Doe"}, headers={"Authorization": "Bearer " + access_token})
 assert response.status_code == 200
 assert response.json()["name"] == "Jane Doe"

def test_delete_contact():
 response = client.post("/auth/register", json={"mobile": "1234567890", "password": "password123"})
 access_token = response.json()["access_token"]
 response = client.post("/contacts", json={"name": "John Doe", "mobile": "1234567890"}, headers={"Authorization": "Bearer " + access_token})
 contact_id = response.json()["id"]
 response = client.delete(f"/contacts/{contact_id}", headers={"Authorization": "Bearer " + access_token})
 assert response.status_code == 200