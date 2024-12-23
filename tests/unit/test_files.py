
import sys
print(sys.path)


import pytest
from unittest.mock import AsyncMock, mock_open, patch
from app.api.v1.endpoints.objects_api import upload_object
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_upload_object_success():
    mock_bucket_repo = AsyncMock()
    mock_bucket_repo.get_bucket_by_name.return_value = {"owner": "test_user"}
    mock_file = mock_open()

    with patch("builtins.open", mock_file), patch("pathlib.Path.mkdir") as mock_mkdir:
        bucket_name = "test_bucket"
        object_key = "test_object"
        file = AsyncMock()
        file.filename = "test_file.txt"
        file.read.return_value = b"File content"
        current_user = AsyncMock()
        current_user.username = "test_user"

        response = await upload_object(
            bucket_name=bucket_name,
            object_key=object_key,
            file=file,
            current_user=current_user,
            bucket_repo=mock_bucket_repo
        )

        assert response["detail"].startswith("Object 'test_object' in bucket 'test_bucket'")
        mock_bucket_repo.get_bucket_by_name.assert_called_once_with("test_bucket")
        mock_file.assert_called_once()
        mock_mkdir.assert_called_once()


@pytest.mark.asyncio
async def test_upload_object_bucket_not_found():
    mock_bucket_repo = AsyncMock()
    mock_bucket_repo.get_bucket_by_name.return_value = None

    bucket_name = "nonexistent_bucket"
    object_key = "test_object"
    file = AsyncMock()
    current_user = AsyncMock()
    current_user.username = "test_user"

    with pytest.raises(HTTPException) as exc:
        await upload_object(
            bucket_name=bucket_name,
            object_key=object_key,
            file=file,
            current_user=current_user,
            bucket_repo=mock_bucket_repo
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "You do not have permission to upload to this bucket"
    mock_bucket_repo.get_bucket_by_name.assert_called_once_with(bucket_name)


@pytest.mark.asyncio
async def test_upload_object_permission_denied():
    mock_bucket_repo = AsyncMock()
    mock_bucket_repo.get_bucket_by_name.return_value = {"owner": "other_user"}

    bucket_name = "test_bucket"
    object_key = "test_object"
    file = AsyncMock()
    current_user = AsyncMock()
    current_user.username = "test_user"

    with pytest.raises(HTTPException) as exc:
        await upload_object(
            bucket_name=bucket_name,
            object_key=object_key,
            file=file,
            current_user=current_user,
            bucket_repo=mock_bucket_repo
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "You do not have permission to upload to this bucket"
    mock_bucket_repo.get_bucket_by_name.assert_called_once_with(bucket_name)


@pytest.mark.asyncio
async def test_upload_object_filesystem_error():
    mock_bucket_repo = AsyncMock()
    mock_bucket_repo.get_bucket_by_name.return_value = {"owner": "test_user"}

    bucket_name = "test_bucket"
    object_key = "test_object"
    file = AsyncMock()
    file.filename = "test_file.txt"
    current_user = AsyncMock()
    current_user.username = "test_user"

    with patch("builtins.open", side_effect=OSError("Filesystem error")), pytest.raises(HTTPException) as exc:
        await upload_object(
            bucket_name=bucket_name,
            object_key=object_key,
            file=file,
            current_user=current_user,
            bucket_repo=mock_bucket_repo
        )

    assert exc.value.status_code == 500
    assert "Filesystem error" in exc.value.detail