from fastapi.testclient import TestClient
from main import app
from pydantic import BaseModel
import httpx

class Contact(BaseModel):
    id: int
    name: str
    mobile: str
    owner_id: int

class ContactCreate(BaseModel):
    name: str
    mobile: str

token = None

def test_get_contacts):
    # test get contacts
    pass

def test_create_contact):
    # test create contact
    pass

def test_get_contact):
    # test get contact
    pass

def test_update_contact):
    # test update contact
    pass

def test_delete_contact):
    # test delete contact
    pass
