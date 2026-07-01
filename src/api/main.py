from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient

from src.cache.redis import RedisCacheStore
from src.db.sqlalchemy.core import db_session_maker
from src.db.sqlalchemy.middleware import DbSessionMiddleware
from src.cryptography.services import DefaultCryptographyService
from src.cryptography.encryption import encrypt, decrypt
from src.cryptography.hashing import deterministic_hash, hash_password, verify_password
from src.object_storage.aws.object_store import AwsObjectStore
from src.vector_store.qdrant.vector_store import QdrantVectorStore
from src.settings import settings
from .router import router as api_router
from .exception_hanlder import ExceptionHanlder


@asynccontextmanager
async def lifespan(app: FastAPI):
    cache_store = RedisCacheStore(connection_url=settings.REDIS_URL)
    app.state.cache_store = cache_store

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

    app.state.object_store = AwsObjectStore(
        bucket_name=settings.AWS_BUCKET_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION_NAME
    )

    vector_store = QdrantVectorStore(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
        collection_name=settings.QDRANT_COLLECTION_NAME
    )
    app.state.vector_store = vector_store

    try:
        yield

    finally:
        await cache_store.close_connection()
        await app.state.ghl_http.aclose()
        await vector_store.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_methods="*",
    allow_origins=settings.ALLOW_ORIGINS,
    allow_headers=["*"]
)

app.add_middleware(DbSessionMiddleware, session_maker=db_session_maker)

app.add_middleware(ExceptionHanlder)

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
