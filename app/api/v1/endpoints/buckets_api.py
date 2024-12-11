from fastapi import APIRouter

bucket_router = APIRouter()


@bucket_router.get("/")
async def get_buckets():
    pass

@bucket_router.put("/{bucket_name}")
async def create_bucket(bucket_name: str):
    pass

@bucket_router.delete("/{bucket_name}")
async def delete_bucket(bucket_name: str):
    pass