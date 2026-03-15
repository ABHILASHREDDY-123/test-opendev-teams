from backend.main import app
from httpx import AsyncClient
import pytest

class TestAuth:
 @pytest.mark.asyncio
 async def test_register_success(self):
 async with AsyncClient(app=app, base_url='http://test') as ac:
 response = await ac.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
 assert response.status_code == 200

 @pytest.mark.asyncio
 async def test_register_duplicate_mobile(self):
 async with AsyncClient(app=app, base_url='http://test') as ac:
 await ac.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
 response = await ac.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
 assert response.status_code == 409

 @pytest.mark.asyncio
 async def test_login_success(self):
 async with AsyncClient(app=app, base_url='http://test') as ac:
 await ac.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
 response = await ac.post('/auth/login', json={'mobile': '1234567890', 'password': 'password'})
 assert response.status_code == 200

 @pytest.mark.asyncio
 async def test_login_wrong_password(self):
 async with AsyncClient(app=app, base_url='http://test') as ac:
 await ac.post('/auth/register', json={'mobile': '1234567890', 'password': 'password'})
 response = await ac.post('/auth/login', json={'mobile': '1234567890', 'password': 'wrongpassword'})
 assert response.status_code == 401

 @pytest.mark.asyncio
 async def test_login_unknown_mobile(self):
 async with AsyncClient(app=app, base_url='http://test') as ac:
 response = await ac.post('/auth/login', json={'mobile': '1234567890', 'password': 'password'})
 assert response.status_code == 401