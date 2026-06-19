from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.cache.redis import RedisCacheStore
from src.settings import settings
from .router import router as api_router



async def lifespan(app: FastAPI):
    cache_store = RedisCacheStore(connection_url=settings.REDIS_URL)
    app.state.cache_store = cache_store

    try:
        yield
    
    finally:
        await cache_store.close_connection()


app = FastAPI(lifespan=lifespan)

@app.get("/")
def health_check():
    return {"status": "ok"}


app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app="src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
