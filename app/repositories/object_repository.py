from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from core.config import settings
from db import get_db
from exceptions.sql_error import SqlError
from models.object import Object
from repositories.bucket_repository import logger

root_dir = settings.fileStorage.root_dir

class ObjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_object(self, bucket_name: str, object_key: str, owner: str, content: str):
        try:
            new_object = Object(
                bucket=bucket_name,
                object_key=object_key,
                owner=owner,
                file_storage_path=f"{root_dir}/{bucket_name}/{object_key}",
                content=content,
                created_at=datetime.now()
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


    async def delete_object(self, bucket_name: str, object_key: str):
        try:
            object_to_delete = await self.session.execute(
                select(Object).where(Object.bucket == bucket_name, Object.object_key == object_key)
            )
            object = object_to_delete.scalar_one_or_none()

            if object:
                await self.session.delete(object)
                await self.session.commit()
                logger.info(f"Object '{object_key}' in bucket '{bucket_name}' deleted successfully.")
            else:
                logger.warn(f"Object '{object_key}' in bucket '{bucket_name}' not found.")
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting object: {e}")
            raise SqlError(f"Error deleting object: {e}")

async def get_object_repository(session: AsyncSession = Depends(get_db)) -> ObjectRepository:
    return ObjectRepository(session)
