import unittest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse

class TestUserRepository(unittest.IsolatedAsyncioTestCase):

    @patch('app.repositories.user_repository.UserRepository.create_user', new_callable=AsyncMock)
    async def test_create_user(self, mock_create_user):
        mock_create_user.return_value = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword",
            created_at=datetime.now(),
            is_active=True
        )

        user_repo = UserRepository(session=None)
        user = await user_repo.create_user(username="testuser", email="test@example.com", password="hashedpassword")

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.is_active)
        mock_create_user.assert_called_once_with(username="testuser", email="test@example.com", password="hashedpassword")

    @patch('app.repositories.user_repository.UserRepository.get_user', new_callable=AsyncMock)
    async def test_get_user(self, mock_get_user):
        mock_get_user.return_value = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword",
            created_at=datetime.now(),
            is_active=True
        )

        user_repo = UserRepository(session=None)
        user = await user_repo.get_user(username="testuser")

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.is_active)
        mock_get_user.assert_called_once_with("testuser")

    @patch('app.repositories.user_repository.UserRepository.update_user', new_callable=AsyncMock)
    async def test_update_user(self, mock_update_user):
        mock_update_user.return_value = User(
            id=1,
            username="updateduser",
            email="updated@example.com",
            hashed_password="hashedpassword",
            created_at=datetime.now(),
            is_active=True
        )

        user_repo = UserRepository(session=None)
        user_update = UserUpdate(username="updateduser", email="updated@example.com")
        user = await user_repo.update_user(user_id=1, user_update=user_update)

        self.assertEqual(user.username, "updateduser")
        self.assertEqual(user.email, "updated@example.com")
        self.assertTrue(user.is_active)
        mock_update_user.assert_called_once_with(user_id=1, user_update=user_update)

    @patch('app.repositories.user_repository.UserRepository.delete_user', new_callable=AsyncMock)
    async def test_delete_user(self, mock_delete_user):
        mock_delete_user.return_value = True

        user_repo = UserRepository(session=None)
        result = await user_repo.delete_user(user_id=1)

        self.assertTrue(result)
        mock_delete_user.assert_called_once_with(user_id=1)

if __name__ == '__main__':
    unittest.main()