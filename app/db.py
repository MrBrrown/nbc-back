#TODO Create repositories instead one db.py
import asyncio
from datetime import datetime
from typing import List
from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy import NullPool, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncSession, \
    async_scoped_session
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from api.v1.endpoints.objects_api import root_dir
from core.config import settings
from models.bucket import Bucket
from models.object import Object
from models.user import User

db_url = settings.db.db_url
# подключение к базе
engine = create_async_engine(url=db_url, echo=True, poolclass=NullPool)

async_session_maker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=True
)


async def get_session():
    async with async_session_maker() as session:
        yield session

class Base(DeclarativeBase):
    pass

async def init_alembic():
    # Путь к файлу alembic.ini
    alembic_cfg_path = 'alembic.ini'
    try:
        # Выполнение миграций
        alembic_cfg = AlembicConfig(alembic_cfg_path)
        await asyncio.to_thread(command.upgrade,alembic_cfg, "head")
    except Exception as e:
        print(f"Error applying Alembic migrations: {e}")

async def create_bucket(bucket_name: str) -> Bucket:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                new_bucket = Bucket(
                    bucket_name=bucket_name,
                    owner="owner",
                    created_at=datetime.now()
                )
                session.add(new_bucket)
                await session.commit()
                return new_bucket
            except Exception as e:
                await session.rollback()
                print(f"Error creating bucket: {e}")





async def delete_bucket (bucket_name: str):
    async with async_session_maker() as session:
        async with session.begin():
            try:
                bucket_to_delete = await session.execute(
                    select(Bucket).where(Bucket.bucket_name == bucket_name)
                )
                bucket = bucket_to_delete.scalar_one_or_none()

                if bucket:
                    await session.delete(bucket)
                    await session.commit()
                    print(f"Bucket '{bucket_name}' deleted successfully.")
                    return True
                else:
                    print(f"Bucket '{bucket_name}' not found.")
                    return False
            except Exception as e:
                await session.rollback()
                print(f"Error deleting bucket: {e}")
                return f"Error: {e}"


def update_bucket(self, bucket_name: str, description: str, content: str):
    pass

async def get_all_buckets():
    async with async_session_maker() as session:
        async with session.begin():
            try:
                result = await session.execute(select(Bucket))
                buckets = result.scalars().all()
                return buckets
            except Exception as e:
                await session.rollback()
                print(f"Error creating bucket: {e}")


async def read_bucket(self, bucket_name: str):
    async with async_session_maker() as session:
        async with session.begin():
            try:
                bucket_to_read = await session.execute(
                    select(Bucket).where(Bucket.bucket_name == bucket_name)
                )
                bucket = bucket_to_read.scalar_one_or_none()

                if bucket:
                    return bucket
                else:
                    print(f"Bucket '{bucket_name}' not found.")
                    return None
            except Exception as e:
                await session.rollback()
                print(f"Error reading bucket: {e}")
                return None
    pass


async def create_object(self, bucket_name: str, object_key: str, owner: str, content: str):
    async with async_session_maker() as session:
        async with session.begin():
            try:
                new_object = Object(
                    bucket=bucket_name,
                    object_key=object_key,
                    owner=owner,
                    file_storage_path=f"{root_dir}/{bucket_name}/{object_key}",
                    content=content,
                    created_at=datetime.now()
                )
                session.add(new_object)
                await session.commit()
                print(f"Object '{object_key}' in bucket '{bucket_name}' created successfully.")
            except Exception as e:
                await session.rollback()
                print(f"Error creating object: {e}")

async def read_object(self, bucket_name: str, object_key: str):
    async with async_session_maker() as session:
        async with session.begin():
            try:
                object_to_read = await session.execute(
                    select(Object).where(Object.bucket == bucket_name, Object.object_key == object_key)
                )
                object = object_to_read.scalar_one_or_none()

                if object:
                    return object
                else:
                    print(f"Object '{object_key}' in bucket '{bucket_name}' not found.")
                    return None
            except Exception as e:
                await session.rollback()
                print(f"Error reading object: {e}")
                return None

async def update_object(self, bucket_name: str, object_key: str, content: str):
    async with async_session_maker() as session:
        async with session.begin():
            try:
                object_to_update = await session.execute(
                    select(Object).where(Object.bucket == bucket_name, Object.object_key == object_key)
                )
                object = object_to_update.scalar_one_or_none()

                if object:
                    object.content = content
                    object.updated_at = datetime.now()
                    await session.commit()
                    print(f"Object '{object_key}' in bucket '{bucket_name}' updated successfully.")
                else:
                    print(f"Object '{object_key}' in bucket '{bucket_name}' not found.")
            except Exception as e:
                await session.rollback()
                print(f"Error updating object: {e}")


async def delete_object(self, bucket_name: str, object_key: str):
    async with async_session_maker() as session:
        async with session.begin():
            try:
                object_to_delete = await session.execute(
                    select(Object).where(Object.bucket == bucket_name, Object.object_key == object_key)
                )
                object = object_to_delete.scalar_one_or_none()

                if object:
                    await session.delete(object)
                    await session.commit()
                    print(f"Object '{object_key}' in bucket '{bucket_name}' deleted successfully.")
                else:
                    print(f"Object '{object_key}' in bucket '{bucket_name}' not found.")
            except Exception as e:
                await session.rollback()
                print(f"Error deleting object: {e}")


async def create_user(self, username: str, email: str, password: str):
    async with async_session_maker() as session:
        async with session.begin():
            try:
                new_user = User(username=username, email=email, password=password)
                session.add(new_user)
                await session.commit()
                print(f"User '{username}' created successfully.")
            except Exception as e:
                await session.rollback()
                print(f"Error creating user: {e}")


async def get_user(self, username: str):
    async with async_session_maker() as session:
        async with session.begin():
            try:
                user_to_read = await session.execute(
                    select(User).where(User.username == username)
                )
                user = user_to_read.scalar_one_or_none()

                if user:
                    return user
                else:
                    print(f"User '{username}' not found.")
                    return None
            except Exception as e:
                await session.rollback()
                print(f"Error reading user: {e}")
                return None


async def update_user(self, username: str, email: str, password: str):
    async with async_session_maker() as session:
        async with session.begin():
            try:
                user_to_update = await session.execute(
                    select(User).where(User.username == username)
                )
                user = user_to_update.scalar_one_or_none()

                if user:
                    user.email = email
                    user.password = password
                    await session.commit()
                    print(f"User '{username}' updated successfully.")
                else:
                    print(f"User '{username}' not found.")
            except Exception as e:
                await session.rollback()
                print(f"Error updating user: {e}")


async def delete_user(self, username: str):
    async with async_session_maker() as session:
        async with session.begin():
            try:
                user_to_delete = await session.execute(
                    select(User).where(User.username == username)
                )
                user = user_to_delete.scalar_one_or_none()

                if user:
                    await session.delete(user)
                    await session.commit()
                    print(f"User '{username}' deleted successfully.")
                else:
                    print(f"User '{username}' not found.")
            except Exception as e:
                await session.rollback()
                print(f"Error deleting user: {e}")
