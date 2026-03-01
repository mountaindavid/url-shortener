from passlib.context import CryptContext
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from jose import jwt
from sqlalchemy.exc import IntegrityError

from app.schemas import UserResponse, UserCreate
from app.config import Settings
from app.dependencies import db_dependency
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = Settings()


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
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
