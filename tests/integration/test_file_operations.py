import pytest
from fastapi.testclient import TestClient
from app.application import get_app


client = TestClient(get_app())


@pytest.fixture
def upload_file():
    bucket_name = "test_bucket"
    object_key = "test_file"
    file_content = b"Sample file content"
    response = client.put(
        f"/{bucket_name}/{object_key}",
        files={"file": ("test.txt", file_content)}
    )
    assert response.status_code == 200
    return bucket_name, object_key


def test_download_file(upload_file):
    bucket_name, object_key = upload_file
    response = client.get(f"/{bucket_name}/{object_key}")
    assert response.status_code == 200
    assert response.content == b"Sample file content"


def test_delete_file(upload_file):
    bucket_name, object_key = upload_file
    response = client.delete(f"/{bucket_name}/{object_key}")
    assert response.status_code == 200
    assert f"Object '{object_key}' in bucket '{bucket_name}' deleted successfully." in response.json()["detail"]
    response = client.get(f"/{bucket_name}/{object_key}")
    assert response.status_code == 404


def test_access_forbidden():
    bucket_name = "other_user_bucket"
    object_key = "some_file"
    response = client.get(f"/{bucket_name}/{object_key}")
    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to download from this bucket"


def test_file_metadata(upload_file):
    bucket_name, object_key = upload_file
    response = client.head(f"/{bucket_name}/{object_key}/metadata")
    assert response.status_code == 200
    assert response.headers["X-File-Name"] == "test.txt"
    assert "X-File-Size-KB" in response.headers
    assert "X-File-Created" in response.headers
    assert "X-File-Modified" in response.headers


def test_list_objects_in_bucket(upload_file):
    bucket_name, _ = upload_file
    response = client.get(f"/{bucket_name}")
    assert response.status_code == 200
    metadata = response.json()
    assert len(metadata) > 0
    assert metadata[0]["name"] == "test.txt"
    assert "size_KB" in metadata[0]
    assert "created" in metadata[0]
    assert "modified" in metadata[0]


def test_invalid_file_name():
    bucket_name = "test_bucket"
    object_key = "invalid:file"
    file_content = b"Invalid file name content"
    response = client.put(
        f"/{bucket_name}/{object_key}",
        files={"file": ("invalid:file.txt", file_content)}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid characters in bucket name or object key"


def test_delete_nonexistent_file():
    bucket_name = "test_bucket"
    object_key = "nonexistent_file"
    response = client.delete(f"/{bucket_name}/{object_key}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Object '{object_key}' in bucket '{bucket_name}' not found."