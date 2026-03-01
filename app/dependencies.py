from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import Annotated

from app.config import Settings
from app.database import get_db
from app.models import User

settings = Settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")
form_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]
db_dependency = Annotated[Session, Depends(get_db)]


def get_current_user(db: db_dependency, token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


user_dependency = Annotated[User, Depends(get_current_user)]
