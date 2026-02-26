from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from app.database import Base


class ShortUrl(Base):
    __tablename__ = 'short_urls'
    id = Column(Integer, primary_key=True)
    short_code = Column(String, unique=True, index=True)
    original_url = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now)