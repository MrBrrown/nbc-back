from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from app import schemas, crud
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from core.config import settings


SECRET_KEY = "v*s)cbb^rxswc^!6w&cexvkc^5k%#mz*4%_dnl)+$g!pr4c7@g"
ALGORITHM = "HS256"
db_url = settings.db.db_url
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(db_url)):
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
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user
