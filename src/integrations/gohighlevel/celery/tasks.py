import asyncio
from httpx import AsyncClient
from pydantic import SecretStr
from src.workers.celery.app import worker
from src.chats.langgraph.workflows import compile_chat_workflow
from src.chats.state import ChatState
from src.settings import settings
from src.cache.redis import RedisCacheStore
from src.cryptography.encryption import decrypt
from src.llm.langchain.agents import LangchainAgent
from src.llm.langchain.models import Provider
from src.embeddings.openai.service import OpenaiEmbeddingService
from src.vector_store.qdrant.vector_store import QdrantVectorStore

from ..client import GoHighLevelClient


async def _workflow_invoker(state: ChatState, location_id: str):
   cache_store = None
   ghl_http = None
   vector_store = None

   try:
      llm = LangchainAgent(
         model="gpt-4o",
         provider=Provider.OPENAI,
         api_key=SecretStr(settings.OPENAI_API_KEY)
      )

      embedding_service = OpenaiEmbeddingService(
         api_key=settings.OPENAI_API_KEY
      )

      vector_store = QdrantVectorStore(
         url=settings.require_qdrant_url(),
         api_key=settings.QDRANT_API_KEY,
         collection_name=settings.require_qdrant_collection_name()
      )
      await vector_store.ensure_collection(vector_size=embedding_service.dimensions)

      cache_store = RedisCacheStore(connection_url=settings.REDIS_URL)

      ghl_http = AsyncClient(
         base_url="https://services.leadconnectorhq.com",
         timeout=30.0,
      )

      ghl_client = GoHighLevelClient(
         http=ghl_http,
         pit=decrypt(state['credential']),
         location_id=location_id
      )
      conversation_client = ghl_client.conversations
      appointments_client = ghl_client.appointments

      workflow = compile_chat_workflow(
         llm=llm,
         conversation_client=conversation_client,
         appointments_client=appointments_client,
         cache_store=cache_store,
         embedding_service=embedding_service,
         vector_store=vector_store
      )

      return await workflow.ainvoke(state)

   finally:
      if cache_store:
         await cache_store.close_connection()
      if ghl_http:
         await ghl_http.aclose()
      if vector_store:
         await vector_store.close()


@worker.task(name="gohighlevel.invoke_chat_workflow", bind=True, max_retries=3)
def invoke_chat_workflow(
   self,
   state: ChatState,
   location_id: str
):
   try:
      return asyncio.run(_workflow_invoker(state=state, location_id=location_id))

   except Exception as exc:
      raise self.retry(exc=exc, countdown=5)
