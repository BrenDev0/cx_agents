from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class UploadedDocumentResponse(BaseModel):
    id: UUID
    name: str
    file_type: str
    url: str
    created_at: datetime