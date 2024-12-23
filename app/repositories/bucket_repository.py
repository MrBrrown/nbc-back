from datetime import datetime
from typing import List

import structlog
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import get_db
from exceptions.sql_error import SqlError
from models.bucket import Bucket
from schemas import BucketSchema

logger = structlog.get_logger()

class BucketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_bucket(self, bucket_name: str, owner: str) -> BucketSchema:
        try:
            new_bucket = Bucket(
                bucket_name=bucket_name,
                owner=owner,
                created_at=datetime.now()
            )
            self.session.add(new_bucket)
            await self.session.flush()
            bucket_schema = BucketSchema.model_validate(new_bucket)
            await self.session.commit()
            logger.info(f"Bucket '{bucket_name}' created successfully.")
            return bucket_schema
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating bucket: {e}")
            raise SqlError(f"Error creating bucket: {e}")

    async def delete_bucket(self,
                            bucket_name: str,
                            owner_username: str) -> bool:
        try:
            bucket = await self.read_bucket(bucket_name)
            if bucket and bucket.owner == owner_username:
                await self.session.delete(bucket)
                await self.session.commit()
                logger.info(f"Bucket '{bucket_name}' deleted successfully.")
                return True
            elif bucket:
                logger.warning(f"Attempt to delete bucket '{bucket_name}' by non-owner '{owner_username}'")
                return False
            return False
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting bucket: {e}")
            raise SqlError(f"Error deleting bucket: {e}")

    async def get_all_buckets(self):

        try:
            result = await self.session.execute(select(Bucket))
            buckets = result.scalars().all()
            bucket_schemas = [BucketSchema.model_validate(bucket) for bucket in buckets]
            return bucket_schemas

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error getting all buckets: {e}")
            raise SqlError(f"Error getting all buckets: {e}")

    async def read_bucket(self, bucket_name: str):
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

    async def get_bucket_by_name(self, bucket_name: str) -> Bucket:
        async with self.session as session:
            result = await session.execute(select(Bucket).where(Bucket.bucket_name == bucket_name))
            bucket = result.scalars().first()
            return bucket

    async def get_buckets_by_owner(self, owner_username: str) -> List[Bucket]:
        async with self.session as session:
            result = await session.execute(
                select(Bucket).where(Bucket.owner == owner_username)
            )
            buckets = result.scalars().all()
            return buckets


async def get_bucket_repository(session: AsyncSession = Depends(get_db)) -> BucketRepository:
    return BucketRepository(session)

