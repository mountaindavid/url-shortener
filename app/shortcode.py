import random
import string

from sqlalchemy.orm import Session
from app.models import ShortUrl

def generate_short_code(length: int = 5) -> str:
    """Generate a random short code (letters + digits)."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

def get_or_create_short_code(url: str, db: Session, max_attempts: int = 10) -> str:
    """If URL exists in DB, return its short_code. Otherwise create new and return it."""
    existing = db.query(ShortUrl).filter(ShortUrl.original_url == url).first()
    if existing:
        return existing.short_code

    for _ in range(max_attempts):
        short_code = generate_short_code()
        if db.query(ShortUrl).filter(ShortUrl.short_code == short_code).first() is None:
            link = ShortUrl(original_url=url, short_code=short_code)
            db.add(link)
            db.commit()
            return link.short_code

    raise ValueError("Could not generate unique short code")

def get_original_url(short_code: str, db: Session) -> str:
    """Get the original URL from the database."""
    original_url = db.query(ShortUrl).filter(ShortUrl.short_code == short_code).first()
    if original_url:
        return original_url.original_url
    else:
        return None

def get_all_urls(db: Session) -> list[ShortUrl]:
    return db.query(ShortUrl).all()