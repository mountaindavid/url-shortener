from pydantic import BaseModel, HttpUrl, Field

class ShortUrlCreate(BaseModel):
    url: HttpUrl

class ShortUrlResponse(BaseModel):
    short_url: str

class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=30)
    password: str = Field(min_length=8, max_length=100)

class UserResponse(BaseModel):
    id: int
    username: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
