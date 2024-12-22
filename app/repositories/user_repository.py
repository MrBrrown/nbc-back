from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app.models.users_model import User
from app.db import get_db
from fastapi import Depends

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, username: str, email: str, password: str) -> User:
        try:
            new_user = User(username=username, email=email, password=password)
            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)
            return new_user
        except Exception as e:
            await self.session.rollback()
            raise e

    async def get_user(self, username: str) -> User:
        try:
            result = await self.session.execute(select(User).filter(User.username == username))
            return result.scalar_one_or_none()
        except Exception as e:
            await self.session.rollback()
            raise e

    async def update_user(self, username: str, email: str, password: str) -> User:
        try:
            user = await self.get_user(username)
            if user:
                user.email = email
                user.password = password
                await self.session.commit()
                return user
            return None
        except Exception as e:
            await self.session.rollback()
            raise e

    async def delete_user(self, username: str) -> bool:
        try:
            user = await self.get_user(username)
            if user:
                await self.session.delete(user)
                await self.session.commit()
                return True
            return False
        except Exception as e:
            await self.session.rollback()
            raise e

    async def revoke_user_token(self, user_id: int):
        query = update(User).where(User.id == user_id).values(is_active=False)
        await self.session.execute(query)
        await self.session.commit()

async def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)
