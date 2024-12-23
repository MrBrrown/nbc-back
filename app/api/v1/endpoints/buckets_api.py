from typing import List

from fastapi import APIRouter, HTTPException, Depends

from repositories.bucket_repository import BucketRepository, get_bucket_repository
from schemas import BucketResponse
from schemas.user_schema import UserResponse
from services.auth_service import get_current_user

bucket_router = APIRouter()

@bucket_router.get("/", response_model=List[BucketResponse])
async def get_buckets(bucket_repo: BucketRepository = Depends(get_bucket_repository),
                      current_user: UserResponse = Depends(get_current_user)):

    buckets = await bucket_repo.get_buckets_by_owner(current_user.username)
    return buckets

@bucket_router.put("/{bucket_name}")
async def create_bucket(bucket_name: str,
                        bucket_repo: BucketRepository = Depends(get_bucket_repository),
                        current_user: UserResponse = Depends(get_current_user)):
    try:
        bucket = await bucket_repo.create_bucket(bucket_name, current_user.username)
        return bucket
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating bucket: {e}")


@bucket_router.delete("/{bucket_name}")
async def delete_bucket(bucket_name: str,
                        bucket_repo: BucketRepository = Depends(get_bucket_repository),
                        current_user: UserResponse = Depends(get_current_user)
                        )-> dict:
    result = await bucket_repo.delete_bucket(bucket_name, current_user.username)

    if result is True:
        return {"detail": f"Bucket '{bucket_name}' deleted successfully."}
    elif result is None:
        raise HTTPException(status_code=404, detail=f"Bucket '{bucket_name}' not found.")
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this bucket")