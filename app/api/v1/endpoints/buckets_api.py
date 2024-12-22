from fastapi import APIRouter, HTTPException
import db
from schemas.bucket_schema import BucketSchema
from typing import List

bucket_router = APIRouter()

@bucket_router.get("/")
async def get_buckets() -> List[BucketSchema]:
    buckets = await db.get_all_buckets()
    return buckets

@bucket_router.put("/{bucket_name}")
async def create_bucket(bucket_name: str) -> BucketSchema:
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