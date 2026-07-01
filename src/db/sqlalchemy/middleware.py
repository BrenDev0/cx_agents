from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp


class DbSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, session_maker: async_sessionmaker):
        super().__init__(app)
        self.session_maker = session_maker

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        if "/api/v1" not in str(request.url):
            return await call_next(request)

        session = self.session_maker()
        request.state.db = session

        try:
            response = await call_next(request)

            if request.state.db.is_active:
                await request.state.db.commit()

            return response

        except Exception:
            await request.state.db.rollback()
            raise

        finally:
            await request.state.db.close()
