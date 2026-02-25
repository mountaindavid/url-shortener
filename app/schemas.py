from pydantic import BaseModel, HttpUrl

class ShortUrlCreate(BaseModel):
    url: HttpUrl

class ShortUrlResponse(BaseModel):
    short_url: str

