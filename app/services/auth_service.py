from fastapi import Depends, HTTPException, status
from jose import JWTError
from jose import jwt

from core.security import oauth2_scheme, SECRET_KEY, ALGORITHM
from repositories.user_repository import UserRepository, get_user_repository
from schemas.user_schema import UserResponse, TokenData

async def get_current_user(token: str = Depends(oauth2_scheme), user_repo: UserRepository = Depends(get_user_repository)) -> UserResponse:
    #TODO replace with exception not related to HTTP, move raise HTTP exceptions to api controllers
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        raise credentials_exception

    user = await user_repo.get_user(token_data.username)

    try:
        if user is None:
            raise credentials_exception

        user_schema = User.model_validate(user)
        if not user_schema or not user_schema.is_active:
            raise credentials_exception
        return user_schema
    except Exception as e:
        raise credentials_exception