from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models.users_model import User

from app.schemas.user import UserCreate, Token
from app.repositories.user_repository import UserRepository, get_user_repository
from app.routers.auth import get_current_user

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

user_router = APIRouter()

#@user_router.post("/login")
#def login(request: LoginRequest):
#    user = User.get_by_username(request.username)  # Предполагается, что такая функция существует
#    if not user or not verify_password(request.password, user.hashed_password):
#        raise HTTPException(status_code=400, detail="Invalid credentials")
#    access_token = create_access_token(data={"sub": user.username})
#    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(request: LoginRequest, user_repo: UserRepository = Depends(get_user_repository)):
    user = await user_repo.get_user(request.username)
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@user_router.get("/me")
async def get_current_user_data(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/register", response_model=Token)
async def register_user(user: UserCreate, user_repo: UserRepository = Depends(get_user_repository)):
    existing_user = await user_repo.get_user(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_password = get_password_hash(user.password)
    new_user = await user_repo.create_user(user.username, user.email, hashed_password)
    access_token = create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@user_router.get("/logout")
async def logout_user(
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    await user_repo.revoke_user_token(current_user.id)
    return {"message": "Successfully logged out"}

@user_router.put("/{user_id}")
async def update_user(user_id: int):
    pass

@user_router.get("/me/links")
async def get_current_user_objects_links():
    pass

@user_router.get("/me/objects")
async def get_current_user_objects_metadata():
    pass
