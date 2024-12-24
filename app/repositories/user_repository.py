from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from ..models.user import User
from ..db import get_db
from fastapi import Depends
import structlog

from ..exceptions.sql_error import SqlError
from ..schemas.user_schema import UserResponse

logger = structlog.get_logger()

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, username: str, email: str, password: str) -> User:
        try:
            new_user = User(username=username,
                            email=email,
                            hashed_password=password,
                            created_at=datetime.now(),
                            )
            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)
            logger.info(f"User '{username}' created successfully.")
            return new_user
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating user: {e}")
            raise SqlError(f"Error creating user: {e}")

    async def get_user(self, username: str) -> UserResponse or None:
        try:
            result = await self.session.execute(select(User).filter(User.username == username))
            user = result.scalar_one_or_none()
            if user:
                return user
            else:
                logger.warn(f"User '{username}' not found.")
                return None
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error reading user: {e}")
            raise SqlError(f"Error reading user: {e}")

    async def update_user(self, username: str, email: str, password: str) -> User:
        try:
            user = await self.get_user(username)
            if user:
                user.email = email
                user.password = password
                await self.session.commit()
                logger.info(f"User '{username}' updated successfully.")
                return user
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating user: {e}")
            raise SqlError(f"Error updating user: {e}")

    async def delete_user(self, username: str) -> bool:
        try:
            user = await self.get_user(username)
            if user:
                await self.session.delete(user)
                await self.session.commit()
                logger.info(f"User '{username}' deleted successfully.")
                return True

            logger.warn(f"User '{username}' not found.")
            return False
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting user: {e}")
            raise SqlError(f"Error deleting user: {e}")


    async def revoke_user_token(self, user_id: int):
        query = update(User).where(User.id == user_id).values(is_active=False)
        await self.session.execute(query)
        await self.session.commit()


async def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)
