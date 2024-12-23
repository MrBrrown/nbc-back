from fastapi import APIRouter, Depends

from schemas.user_schema import UserResponse
from services.auth_service import get_current_user

user_router = APIRouter()

@user_router.get("/me/links")
# async def get_current_user_objects_links(token: str = Depends(oauth2_scheme)):
async def get_current_user_objects_links(current_user: UserResponse = Depends(get_current_user)):
    #todo select only objects owned by current user
    pass

@user_router.get("/me/objects")
async def get_current_user_objects_metadata(current_user: UserResponse = Depends(get_current_user)):
    #todo select only objects owned by current user
    pass

@user_router.get("/me")
async def get_current_user_data(current_user: UserResponse = Depends(get_current_user)):
    return current_user