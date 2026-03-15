from fastapi.testclient import TestClient
from main import app
from auth import User, Token

client = TestClient(app)

class TestAuth:
 def test_register(self):
 # Implement test for user registration
 pass
 
 def test_login(self):
 # Implement test for user login
 pass