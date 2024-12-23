import pytest
from sqlalchemy import select
from app.repositories.bucket_repository import BucketRepository
from app.models.bucket_model import Bucket

@pytest.mark.asyncio
async def test_create_bucket(async_session):

    repo = BucketRepository(async_session)
    bucket = await repo.create_bucket(bucket_name="test_bucket", owner="tester")
    
    assert bucket.bucket_name == "test_bucket"
    assert bucket.owner == "tester"

@pytest.mark.asyncio
async def test_delete_bucket(async_session):
    
    repo = BucketRepository(async_session)
    # Сначала создаем бакет для удаления
    bucket = await repo.create_bucket(bucket_name="delete_bucket", owner="tester")
    
    # Теперь удаляем его
    result = await repo.delete_bucket("delete_bucket")
    assert result is True

    # Проверяем, что бакет действительно удален
    result = await async_session.execute(
        select(Bucket).where(Bucket.bucket_name == "delete_bucket")
    )
    deleted_bucket = result.scalar_one_or_none()
    assert deleted_bucket is None
