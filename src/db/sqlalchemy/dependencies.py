from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

def get_db_session(request: Request) -> AsyncSession:
    db = getattr(request.state, "db", None)
    if not db:
        raise ValueError("Error getting db session")
    
    return db