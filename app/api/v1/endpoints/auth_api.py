from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from ....core.security import create_access_token, verify_password, get_password_hash

from ....schemas.user_schema import UserCreate, Token, UserResponse
from ....repositories.user_repository import UserRepository, get_user_repository
from ....services.auth_service import get_current_user

auth_router = APIRouter()


@auth_router.post("/register", response_model=Token)
async def register_user(user: UserCreate, user_repo: UserRepository = Depends(get_user_repository)):
    existing_user = await user_repo.get_user(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_password = get_password_hash(user.password)
    new_user = await user_repo.create_user(user.username, user.email, hashed_password)
    access_token = create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), user_repo: UserRepository = Depends(get_user_repository)):
    user = await user_repo.get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# @auth_router.get("/logout")
# async def logout_user(
#     current_user: User = Depends(get_current_user),
#     user_repo: UserRepository = Depends(get_user_repository)
# ):
#     await user_repo.revoke_user_token(current_user.id)
#     return {"message": "Successfully logged out"}
