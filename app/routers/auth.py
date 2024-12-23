from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from app import schemas, crud
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from core.config import settings

db_url = settings.db.db_url

SECRET_KEY = "gf10bvs4hwbb#0$mt^3ovzfyrqv3&&bogyoreq00qhi*@q)los"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), user_repo: UserRepository = Depends()):
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
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await user_repo.get_user_by_username(token_data.username)
    if not user or not user.is_active:
        raise credentials_exception
    return user
