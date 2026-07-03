import asyncio
from uuid import UUID

from src.workers.celery.app import worker
from src.settings import settings
from src.db.sqlalchemy.core import worker_session_maker
from src.documents.sqlalchemy.repository import get_by_id as get_document_by_id
from src.object_storage.aws.object_store import AwsObjectStore
from src.embeddings.openai.service import OpenaiEmbeddingService
from src.embeddings.chunking import chunk_text
from src.vector_store.qdrant.vector_store import QdrantVectorStore

from ..sqlalchemy.repository import update_status
from ..models import KnowledgeStatus
from ..pdf import extract_text_from_pdf

EMBEDDING_BATCH_SIZE = 100


async def _process_knowledge(
    knowledge_id: str,
    document_id: str,
    assistant_id: str,
    user_id: str
) -> None:
    db = worker_session_maker()
    vector_store = None

    try:
        document = await get_document_by_id(db=db, document_id=UUID(document_id), user_id=UUID(user_id))

        if not document:
            raise ValueError(f"Document {document_id} not found for user {user_id}")

        object_store = AwsObjectStore(
            bucket_name=settings.AWS_BUCKET_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME,
            endpoint=settings.BUCKET_ENDPOINT
        )
        embedding_service = OpenaiEmbeddingService(api_key=settings.OPENAI_API_KEY)
        vector_store = QdrantVectorStore(
            url=settings.require_qdrant_url(),
            api_key=settings.QDRANT_API_KEY,
            collection_name=settings.require_qdrant_collection_name()
        )
        await vector_store.ensure_collection(vector_size=embedding_service.dimensions)

        metadata = {
            "user_id": user_id,
            "document_id": document_id,
            "assistant_id": assistant_id
        }

        # Clears any vectors left behind by a previous failed attempt so retries stay idempotent.
        await vector_store.delete_by_filter(metadata)

        file_bytes = await object_store.download(document.key)
        text = extract_text_from_pdf(file_bytes)

        if not text.strip():
            raise ValueError(f"No extractable text found in document {document_id}")

        chunks = chunk_text(text)

        for i in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
            batch = chunks[i:i + EMBEDDING_BATCH_SIZE]
            embedding_result = await embedding_service.embed_chunks(batch, metadata=metadata)
            await vector_store.upsert(embedding_result)

        await update_status(db=db, knowledge_id=UUID(knowledge_id), status=KnowledgeStatus.READY)
        await db.commit()

    except Exception:
        try:
            await db.close()
        except Exception:
            pass

        db = worker_session_maker()
        await update_status(db=db, knowledge_id=UUID(knowledge_id), status=KnowledgeStatus.FAILED)
        await db.commit()
        raise

    finally:
        await db.close()
        if vector_store:
            await vector_store.close()


@worker.task(name="knowledge_base.add_document", bind=True, max_retries=3)
def add_document_to_knowledge_base(
    self,
    knowledge_id: str,
    document_id: str,
    assistant_id: str,
    user_id: str
):
    try:
        asyncio.run(_process_knowledge(knowledge_id, document_id, assistant_id, user_id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
