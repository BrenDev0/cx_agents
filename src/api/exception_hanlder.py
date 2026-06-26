import logging
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from fastapi import status
from fastapi.responses import JSONResponse
from ..exceptions import ExceptionCategory, AppError

logger = logging.getLogger(__name__)


_STATUS_CODE_MAP: dict[ExceptionCategory, int] = {
    ExceptionCategory.FORBIDDEN: status.HTTP_403_FORBIDDEN,
    ExceptionCategory.UNAUTHORIZED: status.HTTP_401_UNAUTHORIZED,
    ExceptionCategory.UNPROCESSABLE: status.HTTP_422_UNPROCESSABLE_CONTENT,
    ExceptionCategory.CONFLICT: status.HTTP_409_CONFLICT,
    ExceptionCategory.NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ExceptionCategory.BAD_REQUEST: status.HTTP_400_BAD_REQUEST,
}


class ExceptionHanlder(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        try: 
            response = await call_next(request)


        except AppError as e:
            response = JSONResponse(
                status_code=_STATUS_CODE_MAP[e.category],
                content={"detail": [{"msg": e.detail}]}
            )

        except Exception as e:
            logger.error(e)
            response = JSONResponse(
                status_code=500,
                content={"detial": [{"msg": "Unable to process request at this time"}]}
            )
        
        return response
