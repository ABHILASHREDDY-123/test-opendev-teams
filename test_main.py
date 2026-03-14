import pytest
from fastapi.testclient import TestClient
from backend.app import app, tasks

client = TestClient(app)

def test_get_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []

def test_create_task():
    task_data = {"id": 1, "title": "Test", "description": "Test task"}
    response = client.post("/tasks", json=task_data)
    assert response.status_code == 200
    assert response.json() == {"id": 0}

def test_update_task():
    # Create task
    client.post("/tasks", json={"id": 1, "title": "Old", "description": "Old"})
    # Update task
    response = client.put("/tasks/0", json={"id": 1, "title": "New", "description": "New"})
    assert response.status_code == 200
    response = client.get("/tasks")
    assert response.json()[0]["title"] == "New"

def test_delete_task():
    # Create task
    client.post("/tasks", json={"id": 1, "title": "Delete", "description": "Delete"})
    # Delete task
    response = client.delete("/tasks/0")
    assert response.status_code == 200
    response = client.get("/tasks")
    assert len(response.json()) == 0