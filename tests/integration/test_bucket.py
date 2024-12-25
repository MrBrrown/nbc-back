import pytest
from fastapi.testclient import TestClient
from app.application import get_app
from app.api.v1.endpoints.auth_api import create_access_token

class MockBucketRepo:
    def __init__(self):
        self.buckets = []

    async def create_bucket(self, bucket_name: str, owner_name: str):
        bucket = {"bucket_name": bucket_name, "owner_name": owner_name}
        self.buckets.append(bucket)
        return bucket

    async def delete_bucket(self, bucket_name: str, owner_name: str):
        self.buckets = [
            bucket
            for bucket in self.buckets
            if not (bucket["bucket_name"] == bucket_name and bucket["owner_name"] == owner_name)
        ]

    async def get_buckets_for_user(self, owner_name: str):
        return [bucket for bucket in self.buckets if bucket["owner_name"] == owner_name]


@pytest.fixture
def mock_bucket_repo():
    return MockBucketRepo()


@pytest.fixture
def auth_token():
    return create_access_token(data={"sub": "user"})


@pytest.fixture
def mock_current_user():
    return {
        "username": "user",
        "email": "user@example.com",
        "password": "useruser",
    }


@pytest.fixture
def client(mock_bucket_repo):
    app = get_app()
    app.dependency_overrides[MockBucketRepo] = lambda: mock_bucket_repo
    return TestClient(app)


def test_create_bucket(client, mock_current_user, mock_bucket_repo, auth_token):
    bucket_name = "my-super-puper-storage2"
    create_response = client.put(
        f"/{bucket_name}",
        json={"bucket_name": bucket_name},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert create_response.status_code == 200
    assert create_response.json()["bucket_name"] == bucket_name
    assert create_response.json()["owner_name"] == mock_current_user["username"]



def test_create_bucket_with_invalid_name(client, mock_current_user, mock_bucket_repo, auth_token):
    invalid_bucket_name = "my#bucket@name"
    response = client.put(
        f"/{invalid_bucket_name}",
        json={"bucket_name": invalid_bucket_name},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 500


def test_create_bucket_with_invalid_token(client):
    bucket_name = "my-storage"
    response = client.put(
        f"/{bucket_name}",
        json={"bucket_name": "my_storage"},
        headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401


def test_create_bucket_without_auth(client):
    bucket_name = "my-storage"
    response = client.put(
        f"{bucket_name}",
        json={"bucket_name": "my_storage"},
        headers={}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_buckets_for_user(client, mock_current_user, mock_bucket_repo, auth_token):
    mock_bucket_repo.buckets = [
        {"bucket_name": "my-storage", "owner_name": mock_current_user["username"]}
    ]

    response = client.get(
        "/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    buckets = response.json()

    assert response.status_code == 200


def test_delete_bucket(client, mock_current_user, mock_bucket_repo, auth_token):
    mock_bucket_repo.buckets = [
        {"bucket_name": "my_storage2", "owner_name": mock_current_user["username"]}
    ]

    bucket_name = "my-storage2"
    response = client.delete(
        f"/{bucket_name}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert not any(bucket for bucket in mock_bucket_repo.buckets if bucket["bucket_name"] == bucket_name)


def test_delete_bucket_of_another_user(client, mock_current_user, mock_bucket_repo, auth_token):
    mock_bucket_repo.buckets = [
        {"bucket_name": "user1_bucket", "owner_name": "user1"},
        {"bucket_name": "user2_bucket", "owner_name": mock_current_user["username"]}
    ]

    bucket_name = "user1_bucket"
    response = client.delete(
        f"/{bucket_name}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to delete this bucket"