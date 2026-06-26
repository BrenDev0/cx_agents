from enum import StrEnum

class ExceptionCategory(StrEnum):
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not found"
    CONFLICT = "conflict"
    UNPROCESSABLE = "unprocessable"
    UNAUTHORIZED = "unauthorized"
    BAD_REQUEST = "bad request"
    BLOCKED = "blocked"



class AppError(Exception):
    def __init__(self, detail: str, category: ExceptionCategory):
        super().__init__(detail)
        self.detail = detail
        self.category =  category


class UnauthorizedException(AppError):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(detail=detail, category=ExceptionCategory.UNAUTHORIZED)

class NotFoundException(AppError):
    def __init__(self, detail: str = "Not found"):
        super().__init__(detail=detail, category=ExceptionCategory.NOT_FOUND)

class ForbiddenException(AppError):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(detail=detail, category=ExceptionCategory.FORBIDDEN)

class BadRequestException(AppError):
    def __init__(self, detail: str = "Bad Request"):
        super().__init__(detail=detail, category=ExceptionCategory.BAD_REQUEST)

class RequestBlockedException(AppError):
    def __init__(self, detail: str = "Too many requests"):
        super().__init__(detail=detail, category=ExceptionCategory.BLOCKED)