from fastapi.testclient import TestClient
from app.application import get_app

def test_register_user():
    client = TestClient(get_app())
    
    user_data = {
        "username": "testuser5",
        "email": "user@example.com",
        "password": "strongpassword"
    }
    
    response = client.post("/auth/register", json=user_data)
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_register_user_already_exists():
    client = TestClient(get_app())

    user_data = {
        "username": "testuser",
        "email": "user@example.com",
        "password": "strongpassword"
    }
    client.post("/auth/register", json=user_data)

    response = client.post("/auth/register", json=user_data)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already taken"


def test_login_user():
    client = TestClient(get_app())
    
    user_data = {
        "username": "testuser",
        "password": "strongpassword"
    }
    client.post("/auth/register", json=user_data)
    
    login_data = {
        "username": "testuser",
        "password": "strongpassword"
    }
    response = client.post("/auth/login", data=login_data)
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_user_invalid_credentials():
    client = TestClient(get_app())

    login_data = {
        "username": "invaliduser",
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", data=login_data)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"


def test_get_current_user():
    client = TestClient(get_app())
    
    user_data = {
        "username": "testuser6",
        "email": "user@example.com",
        "password": "strongpassword"
    }
    
    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code == 200, f"Registration failed: {register_response.json()}"
    
    response_data = register_response.json()
    assert "access_token" in response_data, "access_token not found in registration response"
    access_token = response_data["access_token"]
    
    response = client.get("/users/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    response_data = response.json()
    assert response_data["username"] == user_data["username"]


def test_get_current_user_objects():
    client = TestClient(get_app())

    user_data = {
        "username": "testuser7",
        "email": "user@example.com",
        "password": "strongpassword"
    }

    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code == 200, f"Registration failed: {register_response.json()}"
    
    response_data = register_response.json()
    assert "access_token" in response_data, "access_token not found in registration response"
    access_token = response_data["access_token"]

    response = client.get("/users/me/objects", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"


def test_get_current_user_links():
    client = TestClient(get_app())

    user_data = {
        "username": "testuser8",
        "email": "user@example.com",
        "password": "strongpassword"
    }

    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code == 200, f"Registration failed: {register_response.json()}"
    
    response_data = register_response.json()
    assert "access_token" in response_data, "access_token not found in registration response"
    access_token = response_data["access_token"]

    response = client.get("/users/me/links", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"


def test_get_current_user_unauthorized():
    client = TestClient(get_app())
    
    response = client.get("/users/me")
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"