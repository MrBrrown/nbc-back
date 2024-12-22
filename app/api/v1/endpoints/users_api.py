from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.core.security import create_access_token, verify_password
from models.users_model import User

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

user_router = APIRouter()

@user_router.post("/login")
def login(request: LoginRequest):
    user = User.get_by_username(request.username)  # Предполагается, что такая функция существует
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@user_router.get("/me")
async def get_current_user():
    pass

@user_router.post("/register")
async def register_user():
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
