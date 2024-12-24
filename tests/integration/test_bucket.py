import pytest
from fastapi.testclient import TestClient
from app.application import get_app
from app.api.v1.endpoints.auth_api import create_access_token
from app.models.user import User

class MockBucketRepo:
    def __init__(self):
        self.buckets = []

    async def create_bucket(self, bucket_name: str, owner_name: str):
        bucket = {"bucket_name": bucket_name, "owner_name": owner_name}
        self.buckets.append(bucket)
        return bucket
    
    async def delete_bucket(self, bucket_name: str, owner_name: str):
        self.buckets = [bucket for bucket in self.buckets if not (bucket["bucket_name"] == bucket_name and bucket["owner_name"] == owner_name)]
    
    async def get_buckets_for_user(self, owner_name: str):
        return [bucket for bucket in self.buckets if bucket["owner_name"] == owner_name]
    
    async def get_bucket_by_name(self, bucket_name: str, owner_name: str):
        for bucket in self.buckets:
            if bucket["bucket_name"] == bucket_name and bucket["owner_name"] == owner_name:
                return bucket
        return None

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
        "password": "useruser"
    }

def get_mock_bucket_repo():
    return MockBucketRepo()

@pytest.fixture
def client(mock_bucket_repo):
    app = get_app()
    app.dependency_overrides[get_mock_bucket_repo] = lambda: mock_bucket_repo
    return TestClient(app)


def test_get_buckets(client, mock_current_user, mock_bucket_repo, auth_token):
    mock_bucket_repo.create_bucket("bucket1", mock_current_user["username"])
    mock_bucket_repo.create_bucket("bucket2", mock_current_user["username"])

    response = client.get(
        "/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200