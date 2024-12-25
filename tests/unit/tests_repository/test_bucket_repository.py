import os
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.models.bucket import Bucket
from app.models.object import Object
from app.models.user import User
from app.repositories.bucket_repository import BucketRepository, count_files_recursive, get_directory_size
from app.repositories.user_repository import UserRepository
from app.schemas.bucket_schema import BucketCreate
from app.schemas.object_schema import ObjectCreate
from exceptions.sql_error import SqlError

# Mock settings for testing
settings.fileStorage.root_dir = "~/test_root_dir"

@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session

@pytest.fixture
def mock_user_repo():
    user_repo = AsyncMock(spec=UserRepository)
    return user_repo

@pytest.mark.asyncio
async def test_create_bucket_new(mock_session, mock_user_repo):
    # Arrange
    bucket_name = "new_bucket"
    owner_name = "test_user"
    mock_session.execute.return_value.scalar_one_or_none.return_value = (
        None
    )  # No existing bucket
    mock_user_repo.get_user.return_value = User(
        id=1, username=owner_name, email="test@example.com"
    )

    repo = BucketRepository(mock_session, mock_user_repo)

    # Act
    bucket_response = await repo.create_bucket(bucket_name, owner_name)

    # Assert
    assert bucket_response.bucket_name == bucket_name
    assert bucket_response.owner_name == owner_name
    mock_session.add.assert_called()
    mock_session.flush.assert_called()
    mock_session.commit.assert_called()
    mock_session.rollback.assert_not_called()
    mock_user_repo.get_user.assert_awaited_once_with(owner_name)

@pytest.mark.asyncio
async def test_create_bucket_existing(mock_session, mock_user_repo):
    # Arrange
    bucket_name = "existing_bucket"
    owner_name = "test_user"
    existing_bucket = Bucket(
        id=1, bucket_name=bucket_name, owner_id=1, owner_name="old_owner"
    )
    mock_session.execute.return_value.scalar_one_or_none.return_value = (
        existing_bucket
    )

    repo = BucketRepository(mock_session, mock_user_repo)

    # Act
    bucket_response = await repo.create_bucket(bucket_name, owner_name)

    # Assert
    assert bucket_response.bucket_name == bucket_name
    assert bucket_response.owner_name == owner_name  # Updated owner
    mock_session.add.assert_called_with(existing_bucket)
    mock_session.flush.assert_called()
    mock_session.commit.assert_called()
    mock_session.rollback.assert_not_called()
    mock_user_repo.get_user.assert_not_called()  # Should not be called if bucket exists

@pytest.mark.asyncio
async def test_create_bucket_exception(mock_session, mock_user_repo):
    # Arrange
    mock_session.execute.side_effect = SQLAlchemyError("Some error")
    repo = BucketRepository(mock_session, mock_user_repo)

    # Act & Assert
    with pytest.raises(SqlError):
        await repo.create_bucket("any_bucket", "any_user")

    mock_session.rollback.assert_called_once()

@pytest.mark.asyncio
async def test_delete_bucket_success(mock_session, mock_user_repo):
    # Arrange
    bucket_name = "test_bucket"
    owner_username = "test_user"
    bucket = Bucket(
        id=1,
        bucket_name=bucket_name,
        owner_id=1,
        owner_name=owner_username,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    mock_session.execute.return_value.scalar_one_or_none.return_value = bucket
    repo = BucketRepository(mock_session, mock_user_repo)

    # Act
    result = await repo.delete_bucket(bucket_name, owner_username)

    # Assert
    assert result is True
    mock_session.delete.assert_called_once_with(bucket)
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()

@pytest.mark.asyncio
async def test_delete_bucket_not_found(mock_session, mock_user_repo):
    # Arrange
    mock_session.execute.return_value.scalar_one_or_none.return_value = None
    repo = BucketRepository(mock_session, mock_user_repo)

    # Act
    result = await repo.delete_bucket("not_found_bucket", "any_user")

    # Assert
    assert result is False
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_not_called()

@pytest.mark.asyncio
async def test_delete_bucket_exception(mock_session, mock_user_repo):
    # Arrange
    mock_session.execute.side_effect = SQLAlchemyError("Some error")
    repo = BucketRepository(mock_session, mock_user_repo)

    # Act & Assert
    with pytest.raises(SqlError):
        await repo.delete_bucket("any_bucket", "any_user")

    mock_session.rollback.assert_called_once()

@pytest.mark.asyncio
async def test_get_all_buckets(mock_session, mock_user_repo):
    # Arrange
    bucket1 = Bucket(id=1, bucket_name="bucket1", owner_id=1, owner_name="user1")
    bucket2 = Bucket(id=2, bucket_name="bucket2", owner_id=2, owner_name="user2")
    mock_session.execute.return_value.scalars.return_value.all.return_value = [
        bucket1,
        bucket2,
    ]
    repo = BucketRepository(mock_session, mock_user_repo)

    # Act
    buckets = await repo.get_all_buckets()

    # Assert
    assert len(buckets) == 2
    assert buckets[0].bucket_name == "bucket1"
    assert buckets[1].bucket_name == "bucket2"
    mock_session.execute.assert_called_once_with(select(Bucket))
    mock_session.rollback.assert_not_called()

@pytest.mark.asyncio
async def test_get_all_buckets_exception(mock_session, mock_user_repo):
    # Arrange
    mock_session.execute.side_effect = SQLAlchemyError("Some error")
    repo = BucketRepository(mock_session, mock_user_repo)

    # Act & Assert
    with pytest.raises(SqlError):
        await repo.get_all_buckets()

    mock_session.rollback.assert_called_once()

@pytest.mark.asyncio
async def test_read_bucket(mock_session, mock_user_repo):
    # Arrange
    bucket = Bucket(id=1, bucket_name="bucket1", owner_id=1, owner_name="user1")
    mock_session.execute.return_value.scalar_one_or_none.return_value = bucket
    repo = BucketRepository(mock_session, mock_user_repo)

    # Act
    bucket_result = await repo.read_bucket("bucket1")

    # Assert
    assert bucket_result == bucket
    mock_session.execute.assert_called_once()
    mock_session.rollback.assert_not_called()

@pytest.mark.asyncio
async def test_read_bucket_not_found(mock_session, mock_user_repo):
    # Arrange
    mock_session.execute.return_value.scalar_one_or_none.return_value = None
    repo = BucketRepository(mock_session, mock_user_repo)

    # Act
    bucket_result = await repo.read_bucket("bucket1")

    # Assert
    assert bucket_result is None
    mock_session.execute.assert_called_once()
    mock_session.rollback.assert_not_called()

@pytest.mark.asyncio
async def test_read_bucket_exception(mock_session, mock_user_repo):
    # Arrange
    mock_session.execute.side_effect = SQLAlchemyError("Some error")
    repo = BucketRepository(mock_session, mock_user_repo)

    # Act & Assert
    with pytest.raises(SqlError):
        await repo.read_bucket("bucket1")

    mock_session.rollback.assert_called_once()

@pytest.mark.asyncio
async def test_get_bucket_by_name(mock_session, mock_user_repo):
    # Arrange
    bucket = Bucket(id=1, bucket_name="bucket1", owner_id=1, owner_name="user1")
    mock_session.execute.return_value.scalars.return_value.first.return_value = bucket
    repo = BucketRepository(mock_session, mock_user_repo)

    # Act
    bucket_response = await repo.get_bucket_by_name("bucket1")

    # Assert
    assert bucket_response.bucket_name == "bucket1"
    mock_session.execute.assert_called_once_with(
        select(Bucket).where(Bucket.bucket_name == "bucket1")
    )
    mock_session.rollback.assert_not_called()

@pytest.mark.asyncio
async def test_get_bucket_by_name_exception(mock_session, mock_user_repo):
    # Arrange
    mock_session.execute.side_effect = SQLAlchemyError("Some error")
    repo = BucketRepository(mock_session, mock_user_repo)

    # Act & Assert
    with pytest.raises(SqlError):
        await repo.get_bucket_by_name("bucket1")

    mock_session.rollback.assert_called_once()

@pytest.mark.asyncio
@patch(
    "app.api.v1.repositories.bucket_repository.count_files_recursive", return_value=5
)
@patch(
    "app.api.v1.repositories.bucket_repository.get_directory_size", return_value=1024
)
@patch("pathlib.Path.exists")
async def test_get_buckets_by_owner(
    mock_path_exists,
    mock_get_directory_size,
    mock_count_files_recursive,
    mock_session,
    mock_user_repo,
):
    # Arrange
    bucket1 = Bucket(id=1, bucket_name="bucket1", owner_id=1, owner_name="user1")
    bucket2 = Bucket(id=2, bucket_name="bucket2", owner_id=1, owner_name="user1")
    mock_session.execute.return_value.scalars.return_value.all.return_value = [
        bucket1,
        bucket2,
    ]
    repo = BucketRepository(mock_session, mock_user_repo)
    mock_path_exists.return_value = True

    # Act
    buckets = await repo.get_buckets_by_owner("user1")

    # Assert
    assert len(buckets) == 2
    assert buckets[0].bucket_name == "bucket1"
    assert buckets[0].file_count == 5
    assert buckets[0].size == 1024
    mock_session.execute.assert_called_once_with(
        select(Bucket).where(Bucket.owner_name == "user1")
    )
    mock_session.rollback.assert_not_called()

@pytest.mark.asyncio
async def test_get_buckets_by_owner_exception(mock_session, mock_user_repo):
    # Arrange
    mock_session.execute.side_effect = SQLAlchemyError("Some error")
    repo = BucketRepository(mock_session, mock_user_repo)

    # Act & Assert
    with pytest.raises(SqlError):
        await repo.get_buckets_by_owner("user1")

    mock_session.rollback.assert_called_once()

def test_count_files_recursive():
    # Arrange
    with patch("os.walk") as mock_walk:
        mock_walk.return_value = [
            ("/root", ["dir1"], ["file1.txt", "file2.txt"]),
            ("/root/dir1", [], ["file3.txt"]),
        ]

        # Act
        count = count_files_recursive("/root")

        # Assert
        assert count == 3
        mock_walk.assert_called_once_with("/root")

def test_get_directory_size():
    # Arrange
    with patch("os.walk") as mock_walk, patch(
        "os.path.getsize", side_effect=[100, 200, 300]
    ) as mock_getsize:
        mock_walk.return_value = [
            ("/root", ["dir1"], ["file1.txt", "file2.txt"]),
            ("/root/dir1", [], ["file3.txt"]),
        ]

        # Act
        size = get_directory_size("/root")

        # Assert
        assert size == 600
        mock_walk.assert_called_once_with("/root")
        assert mock_getsize.call_count == 3