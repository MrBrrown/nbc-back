import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from loguru import logger
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..db import get_db
from ..core.config import settings
from ..exceptions.sql_error import SqlError
from ..models.bucket import Bucket
from ..repositories.user_repository import UserRepository, get_user_repository
from ..schemas import BucketResponse

root_dir = settings.fileStorage.root_dir

class BucketRepository:
    def __init__(self, session: AsyncSession, user_repo: UserRepository):
        self.session = session
        self.user_repo = user_repo

    async def create_bucket(self, bucket_name: str, owner_name: str) -> BucketResponse:
        try:
            existing_bucket = await self.session.execute(
                select(Bucket).where(Bucket.bucket_name == bucket_name)
            )
            existing_bucket = existing_bucket.scalar_one_or_none()

            if existing_bucket:
                raise HTTPException(status_code=400, detail=f"Bucket with name '{bucket_name}' already exists")

            user = await self.user_repo.get_user(owner_name)

            new_bucket = Bucket(
                bucket_name=bucket_name,
                owner_id=user.id,
                owner_name=user.username,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.session.add(new_bucket)
            await self.session.flush()
            bucket_schema = BucketResponse.model_validate(new_bucket)
            await self.session.commit()

            logger.info(f"Bucket '{bucket_name}' created successfully.")
            return bucket_schema
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating bucket: {e}")
            raise SqlError(f"Error creating bucket: {e}")


    async def delete_bucket(self, bucket_name: str, owner_username: str) -> bool:
        try:
            bucket = await self.session.execute(
                select(Bucket).where(
                    Bucket.bucket_name == bucket_name,
                    Bucket.owner_name == owner_username
                )
            )
            bucket = bucket.scalar_one_or_none()

            if bucket:
                await self.session.delete(bucket)
                await self.session.commit()
                logger.info(f"Bucket '{bucket_name}' deleted successfully by '{owner_username}'.")
                return True
            else:
                logger.warning(f"Bucket '{bucket_name}' not found or access denied for '{owner_username}'.")
                return False
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting bucket: {e}")
            raise SqlError(f"Error deleting bucket: {e}")


    async def get_all_buckets(self):
        try:
            result = await self.session.execute(select(Bucket))
            buckets = result.scalars().all()
            bucket_schemas = [BucketResponse.model_validate(bucket) for bucket in buckets]
            return bucket_schemas

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error getting all buckets: {e}")
            raise SqlError(f"Error getting all buckets: {e}")

    async def read_bucket(self, bucket_name: str) -> Optional[BucketResponse]:
        try:
            bucket_to_read = await self.session.execute(
                select(Bucket).where(Bucket.bucket_name == bucket_name)
            )
            bucket = bucket_to_read.scalar_one_or_none()

            if bucket:
                return bucket
            else:
                logger.warn(f"Bucket '{bucket_name}' not found.")
                return None

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error reading bucket: {e}")
            raise SqlError(f"Error reading bucket: {e}")

    async def get_bucket_by_name(self, bucket_name: str) -> BucketResponse:
        try:
            result = await self.session.execute(select(Bucket).where(Bucket.bucket_name == bucket_name))
            bucket = result.scalars().first()
            logger.info(f"Bucket '{bucket_name}' found successfully.")
            return BucketResponse.model_validate(bucket)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error getting bucket by name: {e}")
            raise SqlError(f"Error getting bucket by name: {e}")


    async def get_buckets_by_owner(self, owner_username: str) -> List[BucketResponse]:
        try:
            result = await self.session.execute(select(Bucket).where(Bucket.owner_name == owner_username))
            buckets = result.scalars().all()
            bucket_schemas = [BucketResponse.model_validate(bucket) for bucket in buckets]
            for bucket_schema in bucket_schemas:
                bucket_schema.file_count = 0
                bucket_schema.size = 0
                path = Path(os.path.join(root_dir, bucket_schema.bucket_name)).expanduser()
                if path.exists():
                    bucket_schema.file_count = count_files_recursive(path)
                    bucket_schema.size = get_directory_size(path)
            logger.info(f"Buckets by owner '{owner_username}' found successfully.")
            return bucket_schemas
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error getting buckets by owner: {e}")
            raise SqlError(f"Error getting buckets by owner: {e}")

async def get_bucket_repository(
    session: AsyncSession = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository)
) -> BucketRepository:
    return BucketRepository(session=session, user_repo=user_repo)

def count_files_recursive(directory):
    """Считает количество файлов в указанной директории, включая вложенные папки."""
    count = 0
    for root, _, files in os.walk(directory):
        count += len(files)
    return count


def get_directory_size(directory):
    """Считает размер директории, включая все вложенные файлы и папки."""
    total_size = 0
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            total_size += os.path.getsize(file_path)
    return total_size
