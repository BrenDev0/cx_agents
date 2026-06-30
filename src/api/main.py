from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import async_sessionmaker
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient

from src.cache.redis import RedisCacheStore
from src.db.sqlalchemy.core import engine
from src.cryptography.services import DefaultCryptographyService
from src.cryptography.encryption import encrypt, decrypt
from src.cryptography.hashing import deterministic_hash, hash_password, verify_password
from src.object_storage.aws.object_store import Aioboto3ObjectStore
from src.settings import settings
from .router import router as api_router
from .exception_hanlder import ExceptionHanlder


@asynccontextmanager
async def lifespan(app: FastAPI):
    cache_store = RedisCacheStore(connection_url=settings.REDIS_URL)
    app.state.cache_store = cache_store

    db_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
    app.state.db_session_maker = db_session_maker

    cryptography_service = DefaultCryptographyService(
        encrypt=encrypt,
        decrypt=decrypt,
        hash_password=hash_password,
        verify_password=verify_password,
        deterministic_hash=deterministic_hash
    )
    app.state.cryptography = cryptography_service


    app.state.ghl_http = AsyncClient(
        base_url="https://services.leadconnectorhq.com",
        timeout=30.0,
    )

    app.state.object_store = Aioboto3ObjectStore(
        bucket_name=settings.AWS_BUCKET_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION_NAME
    )

    try:
        yield
    
    finally:
        await cache_store.close_connection()
        await app.state.ghl_http.aclose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_methods="*",
    allow_origins=settings.ALLOW_ORIGINS,
    allow_headers=["*"]
)

app.add_middleware(ExceptionHanlder)

@app.middleware("http")
async def db_session_middleware(
    request: Request,
    call_next
):
    if "/api/v1" not in str(request.url):
        return await call_next(request)
    
    try:
        session = request.app.state.db_session_maker()
        request.state.db = session

        response = await call_next(request)

        if hasattr(request.state, "db") and request.state.db.is_active:
            await request.state.db.commit()

        return response

    except Exception:
        await request.state.db.rollback()
        await request.state.db.close()
        raise
    
    finally:
        await request.state.db.close()

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
