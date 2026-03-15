from conftest import get_client
import json

def test_create_contact():
 client = get_client()
 response = client.post(
 "_/contacts",
 headers={"Content-Type": "application/json", "Authorization": "Bearer token"},
 data=json.dumps({"name": "Contact 1", "mobile": "1234567890"}),
 )
 assert response.status_code == 200


def test_get_contacts():
 client = get_client()
 response = client.get(
 "_/contacts",
 headers={"Content-Type": "application/json", "Authorization": "Bearer token"},
 )
 assert response.status_code == 200