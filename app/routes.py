from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ShortUrlCreate, ShortUrlResponse
from app.shortcode import get_or_create_short_code, get_original_url, get_all_urls

router = APIRouter()
BASE_URL = "http://localhost:8000"


@router.post("/shorten", status_code=201)
def shorten_url(body: ShortUrlCreate, db: Session = Depends(get_db)) -> ShortUrlResponse:
    original_url_str = str(body.url)
    try:
        short_code = get_or_create_short_code(original_url_str, db)
    except ValueError:
        raise HTTPException(status_code=500, detail="Could not generate unique short code")
    return ShortUrlResponse(short_url=f"{BASE_URL}/{short_code}")


@router.get("/get-all")
def list_all_urls(db: Session = Depends(get_db)):
    return get_all_urls(db)


@router.get("/{short_code}")
def redirect_to_original_url(short_code: str, db: Session = Depends(get_db)):
    original_url = get_original_url(short_code, db)
    if original_url is None:
        raise HTTPException(status_code=404, detail="Short code not found")
    return original_url #temp