from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
from src.cache.types import CacheStore


class RateLimiter(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        limit: int,
        window_seconds: int
    ):
        super().__init__(app)
        
        self._limit = limit
        self._window = window_seconds

    async def dispatch(
        self, 
        request: Request, 
        call_next: RequestResponseEndpoint
    ) -> Response:
        cache_store: CacheStore = request.app.state.cache_store

        ip = self._get_client_ip(request)

        if ip == "unknown":
            return JSONResponse(
                content={"detail": [{"msg": "Unable to process request at this time"}]},
                status_code=403
            )

        request_count_key = f"ratelimit:count:{ip}"
        blocked_ip_key = f"ratelimit:block:{ip}"
        
        is_blocked = await cache_store.get_bool(
            key=blocked_ip_key
        )

        if is_blocked:
            return JSONResponse(
                content={"detail": [{"msg": "Request limit reached"}]},
                status_code=429
            )

        count = await cache_store.increment(key=request_count_key)

        if count == 1:
            await cache_store.expire(key=request_count_key, expire_seconds=self._window)


        if count > self._limit:
            await cache_store.store_bool(
                key=blocked_ip_key,
                data=True,
                expire_seconds=60*10 # 10mins
            )

            return JSONResponse(
                content={"detail": [{"msg": "Request limit reached"}]},
                status_code=429
            )
        
        request.state.ip = ip
        
        return await call_next(request)
    
    
    def _get_client_ip(self, request: Request) -> str:
        ip = "unknown"
        forwarded = request.headers.get("x-forwarded-for")

        if forwarded:
            # Railway's edge proxy is the single trusted hop in front of
            # this service and appends the real peer IP as the last
            # entry. Earlier entries are client-supplied and spoofable.
            ip = forwarded.split(",")[-1].strip()
        else:
            client = request.client
            ip = client.host if client else "unknown"

        return ip
