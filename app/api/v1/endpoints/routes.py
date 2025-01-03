from fastapi import APIRouter

from .auth_api import auth_router
from .objects_api import object_router
from .buckets_api import bucket_router
from .users_api import user_router
from .misc_api import misc_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Authorization"])
api_router.include_router(user_router, prefix="/users", tags=["Users"])
api_router.include_router(misc_router, tags=["Misc"])
api_router.include_router(bucket_router, tags=["Buckets"])
api_router.include_router(object_router, tags=["Objects"])
