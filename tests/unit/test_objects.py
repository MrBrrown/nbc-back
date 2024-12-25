import unittest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from app.models.object import Object
from app.repositories.object_repository import ObjectRepository, get_object_repository
from app.schemas.object_schema import ObjectResponse
from app.repositories.bucket_repository import BucketRepository
from app.repositories.user_repository import UserRepository


class TestObjectRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_session = AsyncMock()
        self.mock_user_repo = AsyncMock(spec=UserRepository)
        self.mock_bucket_repo = AsyncMock(spec=BucketRepository)
        self.object_repo = ObjectRepository(
            session=self.mock_session,
            user_repo=self.mock_user_repo,
            bucket_repo=self.mock_bucket_repo
        )

    @patch('app.repositories.object_repository.ObjectRepository.get_all_objects', new_callable=AsyncMock)
    async def test_get_all_objects(self, mock_get_all_objects):
        # Устанавливаем возвращаемое значение для mock
        mock_get_all_objects.return_value = [ObjectResponse(
            id=1,
            object_key="testkey",
            bucket_name="testbucket",
            owner_name="testuser",
            owner_id=1,
            bucket_id=1,
            file_storage_path="/path/to/file",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            download_url="http://example.com/download",
            size=12345
        )]

        object_repo = ObjectRepository(session=None, user_repo=None, bucket_repo=None)
        objects = await object_repo.get_all_objects(bucket_name=None, username="testuser")

        self.assertEqual(len(objects), 1)
        self.assertEqual(objects[0].object_key, "testkey")
        self.assertEqual(objects[0].bucket_name, "testbucket")
        self.assertEqual(objects[0].owner_name, "testuser")

    @patch('app.repositories.object_repository.ObjectRepository.create_object', new_callable=AsyncMock)
    async def test_create_object(self, mock_create_object):
        object_repo = ObjectRepository(session=None, user_repo=None, bucket_repo=None)
        await object_repo.create_object(
            bucket_name="testbucket",
            object_key="testkey",
            owner_name="testuser",
            extension_without_dot="txt",
            path="/path/to/file",
            download_url="http://example.com/download",
            size=12345
        )

        mock_create_object.assert_called_once_with(
            bucket_name="testbucket",
            object_key="testkey",
            owner_name="testuser",
            extension_without_dot="txt",
            path="/path/to/file",
            download_url="http://example.com/download",
            size=12345
        )

    @patch('app.repositories.object_repository.ObjectRepository.delete_object', new_callable=AsyncMock)
    async def test_delete_object(self, mock_delete_object):
        mock_delete_object.return_value = True

        object_repo = ObjectRepository(session=None, user_repo=None, bucket_repo=None)
        result = await object_repo.delete_object(bucket_name="testbucket", object_key="testkey", username="testuser")

        self.assertTrue(result)
        mock_delete_object.assert_called_once_with(bucket_name="testbucket", object_key="testkey", username="testuser")

    @patch('app.repositories.object_repository.ObjectRepository.read_object', new_callable=AsyncMock)
    async def test_read_object(self, mock_read_object):
        mock_read_object.return_value = ObjectResponse(
            id=1,
            object_key="testkey",
            bucket_name="testbucket",
            owner_name="testuser",
            owner_id=1,
            bucket_id=1,
            file_storage_path="/path/to/file",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            download_url="http://example.com/download",
            size=12345
        )

        object_repo = ObjectRepository(session=None, user_repo=None, bucket_repo=None)
        obj = await object_repo.read_object(bucket_name="testbucket", object_key="testkey", username="testuser")

        self.assertEqual(obj.object_key, "testkey")
        self.assertEqual(obj.bucket_name, "testbucket")
        self.assertEqual(obj.owner_name, "testuser")
        mock_read_object.assert_called_once_with(bucket_name="testbucket", object_key="testkey", username="testuser")




    @patch('app.repositories.object_repository.ObjectRepository.get_object', new_callable=AsyncMock)
    async def test_get_object(self, mock_get_object):
        mock_get_object.return_value = ObjectResponse(
            id=1,
            object_key="testobject",
            bucket_name="testbucket",
            owner_name="testuser",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        obj = await self.object_repo.get_object(bucket_name="testbucket", object_key="testobject")

        self.assertEqual(obj.object_key, "testobject")
        self.assertEqual(obj.bucket_name, "testbucket")
        mock_get_object.assert_called_once_with(bucket_name="testbucket", object_key="testobject")

    @patch('app.repositories.object_repository.ObjectRepository.update_object', new_callable=AsyncMock)
    async def test_update_object(self, mock_update_object):
        mock_update_object.return_value = Object(
            id=1,
            object_key="updatedobject",
            bucket_name="testbucket",
            owner_name="testuser",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        updated_object = await self.object_repo.update_object(
            bucket_name="testbucket",
            object_key="testobject",
            new_key="updatedobject"
        )

        self.assertEqual(updated_object.object_key, "updatedobject")
        mock_update_object.assert_called_once_with(
            bucket_name="testbucket",
            object_key="testobject",
            new_key="updatedobject"
        )



    @patch('app.repositories.object_repository.ObjectRepository.get_object_repository', new_callable=AsyncMock)
    async def test_get_object_repository(self, mock_get_object_repository):
        mock_get_object_repository.return_value = ObjectRepository(
            session=self.mock_session,
            user_repo=self.mock_user_repo,
            bucket_repo=self.mock_bucket_repo
        )



        repo = await get_object_repository()

        self.assertIsInstance(repo, ObjectRepository)
        mock_get_object_repository.assert_called_once()

if __name__ == '__main__':
    unittest.main()