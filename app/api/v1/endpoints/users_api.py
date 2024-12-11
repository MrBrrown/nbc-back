from fastapi import APIRouter

user_router = APIRouter()

@user_router.get("/me")
async def get_current_user():
    pass

@user_router.post("/register")
async def register_user():
    pass

@user_router.post("/login")
async def login_user():
    pass

@user_router.get("/logout")
async def logout_user():
    pass

@user_router.put("/{user_id}")
async def update_user(user_id: int):
    pass

@user_router.get("/me/links")
async def get_current_user_objects_links():
    pass

@user_router.get("/me/objects")
async def get_current_user_objects_metadata():
    pass