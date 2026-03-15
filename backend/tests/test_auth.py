from conftest import get_client
import json

def test_register_success():
 client = get_client()
 response = client.post(
 "_/auth/register",
 headers={"Content-Type": "application/json"},
 data=json.dumps({"username": "user1", "email": "user1@example.com", "full_name": "User 1", "password": "password1"}),
 )
 assert response.status_code == 200


def test_register_duplicate():
 client = get_client()
 response = client.post(
 "_/auth/register",
 headers={"Content-Type": "application/json"},
 data=json.dumps({"username": "user1", "email": "user1@example.com", "full_name": "User 1", "password": "password1"}),
 )
 assert response.status_code == 400


def test_login_success():
 client = get_client()
 response = client.post(
 "_/auth/login",
 headers={"Content-Type": "application/x-www-form-urlencoded"},
 data={"username": "user1", "password": "password1"},
 )
 assert response.status_code == 200


def test_login_wrong_password():
 client = get_client()
 response = client.post(
 "_/auth/login",
 headers={"Content-Type": "application/x-www-form-urlencoded"},
 data={"username": "user1", "password": "wrongpassword"},
 )
 assert response.status_code == 400