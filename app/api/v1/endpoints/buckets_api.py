from fastapi import APIRouter, HTTPException
import app.db as db
from app.schemas.bucket import BucketBase
from typing import List


bucket_router = APIRouter(tags=["Buckets"])


@bucket_router.get("/")
async def get_buckets() -> List[BucketBase]:
    buckets = await db.get_all_buckets()
    return buckets

@bucket_router.post("/{bucket_name}")
async def create_bucket(bucket_name: str) -> BucketBase:
    bucket = await db.create_bucket(bucket_name)
    return bucket


@bucket_router.delete("/{bucket_name}")
async def delete_bucket(bucket_name: str)-> dict:
    result = await db.delete_bucket(bucket_name)
    if result is True:
        return {"detail": f"Bucket '{bucket_name}' deleted successfully."}
    elif result is False:
        raise HTTPException(status_code=404, detail=f"Bucket '{bucket_name}' not found.")
    else:
        raise HTTPException(status_code=500, detail=result)
