from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.schemas import UserResponse, UserCreate
from app.config import Settings
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.database import db_dependency
from app.models import User
from sqlalchemy.exc import IntegrityError
from typing import Annotated
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

settings = Settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")
form_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_user(user: UserCreate, db: db_dependency) -> UserResponse:
    new_user = User(username=user.username, password_hash=hash_password(user.password))
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username already exists")
    db.refresh(new_user)
    return UserResponse(id=new_user.id, username=new_user.username)


def authenticate_user(username: str, password: str, db: db_dependency) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiration)    
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def get_current_user(db: db_dependency, token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
    

user_dependency = Annotated[User, Depends(get_current_user)]