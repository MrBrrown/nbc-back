# tests/unit/test_buckets.py
import unittest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from app.models.bucket import Bucket
from app.repositories.bucket_repository import BucketRepository
from app.schemas.bucket_schema import BucketCreate, BucketResponse, BucketMetadata, BucketStatistics, BucketBase

class TestBucketRepository(unittest.IsolatedAsyncioTestCase):

    @patch('app.repositories.bucket_repository.BucketRepository.create_bucket', new_callable=AsyncMock)
    async def test_create_bucket(self, mock_create_bucket):
        mock_create_bucket.return_value = Bucket(
            id=1,
            name="testbucket",
            owner_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        bucket_repo = BucketRepository(session=None)
        bucket = await bucket_repo.create_bucket(name="testbucket", owner_id=1)

        self.assertEqual(bucket.name, "testbucket")
        self.assertEqual(bucket.owner_id, 1)
        mock_create_bucket.assert_called_once_with(name="testbucket", owner_id=1)

    @patch('app.repositories.bucket_repository.BucketRepository.get_bucket', new_callable=AsyncMock)
    async def test_get_bucket(self, mock_get_bucket):
        mock_get_bucket.return_value = Bucket(
            id=1,
            name="testbucket",
            owner_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        bucket_repo = BucketRepository(session=None)
        bucket = await bucket_repo.get_bucket(bucket_id=1)

        self.assertEqual(bucket.name, "testbucket")
        self.assertEqual(bucket.owner_id, 1)
        mock_get_bucket.assert_called_once_with(bucket_id=1)

    @patch('app.repositories.bucket_repository.BucketRepository.update_bucket', new_callable=AsyncMock)
    async def test_update_bucket(self, mock_update_bucket):
        mock_update_bucket.return_value = Bucket(
            id=1,
            name="updatedbucket",
            owner_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        bucket_repo = BucketRepository(session=None)
        bucket_update = BucketUpdate(name="updatedbucket")
        bucket = await bucket_repo.update_bucket(bucket_id=1, name="updatedbucket")

        self.assertEqual(bucket.name, "updatedbucket")
        self.assertEqual(bucket.owner_id, 1)
        mock_update_bucket.assert_called_once_with(bucket_id=1, name="updatedbucket")

    @patch('app.repositories.bucket_repository.BucketRepository.delete_bucket', new_callable=AsyncMock)
    async def test_delete_bucket(self, mock_delete_bucket):
        mock_delete_bucket.return_value = True

        bucket_repo = BucketRepository(session=None)
        result = await bucket_repo.delete_bucket(bucket_id=1)

        self.assertTrue(result)
        mock_delete_bucket.assert_called_once_with(bucket_id=1)

if __name__ == '__main__':
    unittest.main()