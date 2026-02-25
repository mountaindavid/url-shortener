from fastapi import APIRouter
from app.schemas import ShortUrlCreate, ShortUrlResponse
from app.shortcode import generate_short_code
from fastapi.responses import RedirectResponse
from fastapi import HTTPException

router = APIRouter()

short_codes = {}
original_urls = {}

@router.post('/shorten', status_code=201)
def shorten_url(url: ShortUrlCreate) -> ShortUrlResponse:
    original_url_str = str(url.url)
    if original_url_str in original_urls:
        short_code = original_urls[original_url_str]
    else:
        short_code = generate_short_code()
        while short_code in short_codes:
            short_code = generate_short_code()
        short_codes[short_code] = original_url_str
        original_urls[original_url_str] = short_code
    return ShortUrlResponse(short_url=f'http://localhost:8000/{short_code}')

@router.get('/{short_code}')
def redirect_to_original_url(short_code: str):
    if short_code in short_codes:
        return RedirectResponse(url=short_codes[short_code])
    else:
        raise HTTPException(status_code=404, detail='Short code not found')