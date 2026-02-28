from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from app.database import db_dependency
from app.auth import form_dependency
from app.schemas import ShortUrlCreate, ShortUrlResponse, UserResponse, UserCreate, TokenResponse
from app.shortcode import get_or_create_short_code, get_original_url, get_all_urls
from app.config import Settings
from app.auth import create_user, create_access_token, authenticate_user, user_dependency
from app.models import User

router = APIRouter()
BASE_URL = Settings().base_url


@router.post("/shorten", status_code=201)
def shorten_url(body: ShortUrlCreate, db: db_dependency, current_user: user_dependency) -> ShortUrlResponse:
    original_url_str = str(body.url)
    try:
        short_code = get_or_create_short_code(original_url_str, db)
    except ValueError:
        raise HTTPException(status_code=500, detail="Could not generate unique short code")
    return ShortUrlResponse(short_url=f"{BASE_URL}/{short_code}")


@router.get("/get-all")
def list_all_urls(db: db_dependency, current_user: user_dependency):
    return get_all_urls(db)


@router.get("/{short_code}")
def redirect_to_original_url(short_code: str, db: db_dependency) -> str:
    original_url = get_original_url(short_code, db)
    if original_url is None:
        raise HTTPException(status_code=404, detail="Short code not found")
    return original_url #temporary


@router.post("/auth/register")
def register_user(user: UserCreate, db: db_dependency) -> UserResponse:
    return create_user(user, db)

@router.post("/auth/token")
def get_token(form: form_dependency, db: db_dependency) -> TokenResponse:
    user = authenticate_user(form.username, form.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return TokenResponse(access_token=access_token, token_type="bearer")