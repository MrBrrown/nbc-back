from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from models.bucket import Bucket

class BucketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_bucket(self, bucket_name: str, owner: str) -> Bucket:
        new_bucket = Bucket(
            bucket_name=bucket_name,
            owner=owner,
            created_at=datetime.now()
        )
        self.session.add(new_bucket)
        await self.session.commit()
        return new_bucket

    async def delete_bucket(self, bucket_name: str) -> bool:
        result = await self.session.execute(select(Bucket).where(Bucket.bucket_name == bucket_name))
        bucket = result.scalar_one_or_none()
        if bucket:
            await self.session.delete(bucket)
            await self.session.commit()
            return True
        return False
