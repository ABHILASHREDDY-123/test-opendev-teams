import pytest
from backend.main import app, users_db, contacts_db

@pytest.fixture(autouse=True)
def reset_state():
    users_db.clear()
    contacts_db.clear()
