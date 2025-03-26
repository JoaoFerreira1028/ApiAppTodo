import pytest
from flask import Flask
from AppUsers import app, users_collection, todo_collection  # Import the Flask app

test_user = {
    "username": "testuser",
    "fullname": "Test User",
    "email": "testuser@example.com",
    "password": "password123"
}

test_todo = {
    "title": "Test Task",
    "completed": False
}

@pytest.fixture(autouse=True)
def clean_db():
    """Cleans the database before each test"""
    users_collection.delete_many({"username": test_user["username"]})
    todo_collection.delete_many({})

@pytest.fixture
def user():
    app.config["TESTING"] = True
    with app.test_client() as user:
        yield user

def get_token(user):
    """Performs login and returns the JWT token"""
    response = user.post("/login", json={"username": test_user["username"], "password": test_user["password"]})
    assert response.status_code == 200
    return response.get_json()["access_token"]

# User creation test
def test_create_user(user):
    response = user.post("/users", json=test_user)
    assert response.status_code == 201
    assert "id" in response.get_json()
    assert response.get_json()["message"] == "User created"

# User creation test with invalid data
def test_create_user_invalid_data(user):
    invalid_user = test_user.copy()
    del invalid_user["email"]  # Remove the "email" field
    response = user.post("/users", json=invalid_user)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Incomplete data"

# Login test
def test_login(user):
    user.post("/users", json=test_user)  # Ensure the user exists
    token = get_token(user)
    assert token  # Check that the token was correctly generated

# Login test with invalid data
def test_login_invalid(user):
    response = user.post("/login", json={"username": "wronguser", "password": "wrongpass"})
    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid username or password"

# Task creation test protected with JWT
def test_create_todo(user):
    user.post("/users", json=test_user)
    token = get_token(user)
    headers = {"Authorization": f"Bearer {token}"}
    response = user.post("/todos", json=test_todo, headers=headers)
    assert response.status_code == 201
    assert "id" in response.get_json()
    assert response.get_json()["message"] == "Task created"

# Task listing test protected with JWT
def test_list_todos(user):
    user.post("/users", json=test_user)
    token = get_token(user)
    headers = {"Authorization": f"Bearer {token}"}
    response = user.get("/todos", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

# Task update test
def test_update_todo(user):
    user.post("/users", json=test_user)
    token = get_token(user)
    headers = {"Authorization": f"Bearer {token}"}
    response = user.post("/todos", json=test_todo, headers=headers)
    todo_id = response.get_json()["id"]
    updated_todo = {"title": "Updated Task", "completed": True}
    response = user.put(f"/todos/{todo_id}", json=updated_todo, headers=headers)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Task updated"

# Task deletion test
def test_delete_todo(user):
    user.post("/users", json=test_user)
    token = get_token(user)
    headers = {"Authorization": f"Bearer {token}"}
    response = user.post("/todos", json=test_todo, headers=headers)
    todo_id = response.get_json()["id"]
    response = user.delete(f"/todos/{todo_id}", headers=headers)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Task deleted"

# User deletion test
def test_delete_user(user):
    user.post("/users", json=test_user)
    token = get_token(user)
    headers = {"Authorization": f"Bearer {token}"}
    response = user.delete(f"/users/{test_user['username']}", headers=headers)
    assert response.status_code == 200
    assert response.get_json()["message"] == "User and associated tasks deleted"

# Unauthorized access test
def test_unauthorized_access(user):
    response = user.get("/todos")
    assert response.status_code == 401

# User not found test
def test_get_user_not_found(user):
    response = user.get("/users/nonexistentuser")
    assert response.status_code == 404
    assert response.get_json()["error"] == "User not found"

# Task not found test
def test_get_todo_not_found(user):
    response = user.get("/todos/999999999999999999999999")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Task not found"

# User update test
def test_update_user(user):
    user.post("/users", json=test_user)
    token = get_token(user)
    headers = {"Authorization": f"Bearer {token}"}
    updated_user = {"fullname": "Updated User", "email": "updatedemail@example.com"}
    response = user.put(f"/users/{test_user['username']}", json=updated_user, headers=headers)
    assert response.status_code == 200
    assert response.get_json()["message"] == "User updated"

# User update test with invalid data
def test_update_user_invalid(user):
    user.post("/users", json=test_user)
    token = get_token(user)
    headers = {"Authorization": f"Bearer {token}"}
    invalid_user = {}  # Invalid data, missing "email"
    response = user.put(f"/users/{test_user['username']}", json=invalid_user, headers=headers)
    assert response.status_code == 400
    assert response.get_json()["error"] == "No data provided"

# Task creation validation test with invalid data
def test_create_todo_invalid_data(user):
    user.post("/users", json=test_user)
    token = get_token(user)
    headers = {"Authorization": f"Bearer {token}"}
    invalid_todo = {}  # Invalid data, missing "title"
    response = user.post("/todos", json=invalid_todo, headers=headers)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Incomplete data"
