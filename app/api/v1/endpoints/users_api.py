from urllib.parse import urljoin

from fastapi import APIRouter, Depends
from starlette.requests import Request

from ....repositories.object_repository import ObjectRepository, get_object_repository
from ....schemas.object_schema import ObjectLink
from .objects_api import download_object, ACCESS_KEY, SECRET_KEY, DEFAULT_EXPIRATION_MINUTES, generate_presigned_url
from ....schemas.user_schema import UserResponse
from ....services.auth_service import get_current_user

user_router = APIRouter()

@user_router.get("/me/links")
async def get_current_user_objects_links(current_user: UserResponse = Depends(get_current_user),
                                         obj_repo: ObjectRepository = Depends(get_object_repository),
                                         request: Request = None):
    objects = await obj_repo.get_all_objects(bucket_name=None, username= current_user.username)
    object_links = [ObjectLink(bucket_name=obj.bucket_name, object_key=obj.object_key,
                               download_url=generate_presigned_url(urljoin(str(request.base_url),
                                                                           f"api/v1/presigned/{obj.bucket_name}/{obj.object_key}"),
                                                                   ACCESS_KEY, SECRET_KEY, "GET", obj.bucket_name,
                                                                   obj.object_key, DEFAULT_EXPIRATION_MINUTES)) for obj
                    in objects]
    return object_links

@user_router.get("/me/objects")
async def get_current_user_objects_metadata(current_user: UserResponse = Depends(get_current_user),
                                            obj_repo: ObjectRepository = Depends(get_object_repository)):
    objects = await obj_repo.get_all_objects(bucket_name=None, username=current_user.username)
    return objects

@user_router.get("/me")
async def get_current_user_data(current_user: UserResponse = Depends(get_current_user)):
    return current_user