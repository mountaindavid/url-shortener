from fastapi import FastAPI
from app.routes import router
import uvicorn
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix='/api')

@app.get('/health')
async def health_check():
    return {'status': 'healthy'}

if __name__ == '__main__':
    uvicorn.run("app.main:app", host='0.0.0.0', port=8000, reload=True)