from fastapi import APIRouter, HTTPException, Depends

from repositories.bucket_repository import BucketRepository, get_bucket_repository
from schemas.user_schema import User
from services.auth_service import get_current_user

bucket_router = APIRouter()

@bucket_router.get("/")
async def get_buckets(bucket_repo: BucketRepository = Depends(get_bucket_repository),
                      current_user: User = Depends(get_current_user)):
    #todo select only buckets owned by current user
    buckets = await bucket_repo.get_all_buckets()
    return buckets

@bucket_router.put("/{bucket_name}")
async def create_bucket(bucket_name: str,
                        bucket_repo: BucketRepository = Depends(get_bucket_repository),
                        current_user: User = Depends(get_current_user)):
    try:
        bucket = await bucket_repo.create_bucket(bucket_name, current_user.username)
        return bucket
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating bucket: {e}")


@bucket_router.delete("/{bucket_name}")
async def delete_bucket(bucket_name: str,
                        bucket_repo: BucketRepository = Depends(get_bucket_repository),
                        current_user: User = Depends(get_current_user))-> dict:
    #todo check if bucket is owned by current user
    result = await bucket_repo.delete_bucket(bucket_name)
    if result is True:
        return {"detail": f"Bucket '{bucket_name}' deleted successfully."}
    elif result is False:
        raise HTTPException(status_code=404, detail=f"Bucket '{bucket_name}' not found.")
    else:
        raise HTTPException(status_code=500, detail=result)