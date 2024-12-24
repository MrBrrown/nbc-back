from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from ..core.config import settings
from ..db import get_db
from ..exceptions.sql_error import SqlError
from ..models.object import Object
from ..repositories.bucket_repository import logger, BucketRepository, get_bucket_repository
from ..repositories.user_repository import UserRepository, get_user_repository
from ..schemas.object_schema import ObjectResponse

root_dir = settings.fileStorage.root_dir

class ObjectRepository:
    def __init__(self, session: AsyncSession, user_repo: UserRepository, bucket_repo: BucketRepository):
        self.session = session
        self.user_repo = user_repo
        self.bucket_repo = bucket_repo

    async def get_all_objects(self, bucket_name: str, username: str):
        try:
            objects = await self.session.execute(
                select(Object).where(Object.bucket_name == bucket_name, Object.owner_name == username)
            )
            objects = objects.scalars().all()
            object_schemas = [ObjectResponse.model_validate(obj) for obj in objects]
            logger.info(f"Objects in bucket '{bucket_name}' found successfully.")
            return object_schemas


        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error getting all objects: {e}")
            raise SqlError(f"Error getting all objects: {e}")


    async def create_object(self, bucket_name: str, object_key: str, owner_name: str, extension_without_dot: str,
                            path: str, download_url:str, size: int):
        try:
            user= await self.user_repo.get_user(owner_name)
            bucket = await self.bucket_repo.read_bucket(bucket_name)
            new_object = Object(
                bucket_id=bucket.id,
                bucket_name=bucket_name,
                object_key=object_key,
                owner_id=user.id,
                owner_name=user.username,
                file_storage_path=path,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                download_url=download_url,
                size=size,
                extension=extension_without_dot
            )
            self.session.add(new_object)
            await self.session.commit()
            logger.info(f"Object '{object_key}' in bucket '{bucket_name}' created successfully.")
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating object: {e}")
            raise SqlError(f"Error creating object: {e}")

    async def read_object(self, bucket_name: str, object_key: str):
        try:
            object_to_read = await self.session.execute(
                select(Object).where(Object.bucket == bucket_name, Object.object_key == object_key)
            )
            object = object_to_read.scalar_one_or_none()

            if object:
                return object
            else:
                logger.warn(f"Object '{object_key}' in bucket '{bucket_name}' not found.")
                return None
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error reading object: {e}")
            raise SqlError(f"Error reading object: {e}")

    async def update_object(self, bucket_name: str, object_key: str, content: str):
        try:
            object_to_update = await self.session.execute(
                select(Object).where(Object.bucket == bucket_name, Object.object_key == object_key)
            )
            object = object_to_update.scalar_one_or_none()

            if object:
                object.content = content
                object.updated_at = datetime.now()
                await self.session.commit()
                logger.info(f"Object '{object_key}' in bucket '{bucket_name}' updated successfully.")
            else:
                logger.warn(f"Object '{object_key}' in bucket '{bucket_name}' not found.")
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating object: {e}")
            raise SqlError(f"Error updating object: {e}")


    async def delete_object(self, bucket_name: str, object_key: str, owner_username: str):
        try:
            object_record = await self.session.execute(
                select(Object).where(
                    Object.bucket_name == bucket_name,
                    Object.object_key == object_key,
                    Object.owner_name == owner_username
                )
            )
            object_record = object_record.scalar_one_or_none()

            if object_record:
                await self.session.delete(object_record)
                await self.session.commit()
                logger.info(f"Object '{object_key}' in bucket '{bucket_name}' deleted from database.")
            else:
                logger.warning(f"Object '{object_key}' not found in database.")
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting object: {e}")
            raise SqlError(f"Error deleting object: {e}")


async def get_object_repository(session: AsyncSession = Depends(get_db),
                                user_repo: UserRepository = Depends(get_user_repository),
                                bucket_repo: BucketRepository = Depends(get_bucket_repository)) -> ObjectRepository:
    return ObjectRepository(session=session, user_repo=user_repo, bucket_repo=bucket_repo)