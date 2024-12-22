#TODO Create repositories instead one db.py
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.future import select

from api.v1.endpoints.objects_api import root_dir
from core.config import settings, get_alembic_cfg_path, get_project_root
from models.bucket import Bucket
from models.object import Object
from models.user import User
from schemas.bucket_schema import BucketSchema

db_url = settings.db.db_url
# подключение к базе
engine = create_async_engine(url=db_url, echo=True, poolclass=NullPool)
async_session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=True)

async def init_alembic():
    # Сохраняем текущую рабочую директорию
    current_working_directory = Path.cwd()
    # Путь к файлу alembic.ini
    alembic_cfg_path = get_alembic_cfg_path()
    try:
        os.chdir(get_project_root())
        # Выполнение миграций
        alembic_cfg = AlembicConfig(alembic_cfg_path)
        await asyncio.to_thread(command.upgrade,alembic_cfg, "head")
    except Exception as e:
        print(f"Error applying Alembic migrations: {e}")
    finally:
        # Восстановить текущую рабочую директорию
        os.chdir(current_working_directory)

async def create_bucket(bucket_name: str):
    async with async_session_factory() as session:
        async with session.begin():
            try:
                new_bucket = Bucket(
                    bucket_name=bucket_name,
                    owner="owner",
                    created_at=datetime.now()
                )
                session.add(new_bucket)
                await session.flush()
                bucket_schema = BucketSchema.model_validate(new_bucket)
                await session.commit()
                return bucket_schema
            except Exception as e:
                await session.rollback()
                print(f"Error creating bucket: {e}")

async def delete_bucket (bucket_name: str):
    async with async_session_factory() as session:
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
    async with async_session_factory() as session:
        async with session.begin():
            try:
                result = await session.execute(select(Bucket))
                buckets = result.scalars().all()
                bucket_schemas = [BucketSchema.model_validate(bucket) for bucket in buckets]
                return bucket_schemas
            except Exception as e:
                await session.rollback()
                print(f"Error creating bucket: {e}")


async def read_bucket(self, bucket_name: str):
    async with async_session_factory() as session:
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
    async with async_session_factory() as session:
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
    async with async_session_factory() as session:
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
    async with async_session_factory() as session:
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
    async with async_session_factory() as session:
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
    async with async_session_factory() as session:
        async with session.begin():
            try:
                new_user = User(username=username, email=email, password=password)
                session.add(new_user)
                await session.commit()
                print(f"User '{username}' created successfully.")
            except Exception as e:
                await session.rollback()
                print(f"Error creating user: {e}")


async def read_user(self, username: str):
    async with async_session_factory() as session:
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
    async with async_session_factory() as session:
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
    async with async_session_factory() as session:
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
