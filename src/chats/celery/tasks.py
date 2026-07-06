import asyncio
import json
from httpx import AsyncClient
from pydantic import SecretStr
from src.workers.celery.app import worker
from src.chats.langgraph.workflows import compile_chat_workflow
from src.chats.state import ChatState
from src.settings import settings
from src.cache.redis import RedisCacheStore
from src.integrations.gohighlevel.conversations import GHLConversationsClient
from src.cryptography.encryption import decrypt
from src.db.sqlalchemy.core import worker_session_maker
from src.llm.langchain.agents import LangchainAgent
from src.llm.langchain.models import Provider
from src.embeddings.openai.service import OpenaiEmbeddingService
from src.vector_store.qdrant.vector_store import QdrantVectorStore


async def _workflow_invoker(location_id: str,  state: ChatState):
   try:
      db = None
      cache_store = None
      ghl_http = None
      vector_store = None

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
      db = worker_session_maker()
      agent_credential = ""

      if not agent_credential:
         raise ValueError(f"No credential found for location id: {location_id}")


      ghl_http = AsyncClient(
         base_url="https://services.leadconnectorhq.com",
         timeout=30.0,
      )
      
      ghl_headers = {
         "Authorization": f"Bearer {json.loads(decrypt(agent_credential.payload))['access_token']}",
         "Version": "v3"
      }
      conversation_client = GHLConversationsClient(
         http=ghl_http,
         headers=ghl_headers
      )

      workflow = compile_chat_workflow(
         llm=llm,
         conversation_client=conversation_client,
         cache_store=cache_store,
         embedding_service=embedding_service,
         vector_store=vector_store
      )

      return await workflow.ainvoke(state)

   finally:
      if db:
         await db.close()
      if cache_store:
         await cache_store.close_connection()
      if ghl_http:
         await ghl_http.aclose()
      if vector_store:
         await vector_store.close()
   


@worker.task(name="chats.invoke_workflow", bind=True, max_retries=3)
def invoke_chat_workflow(
   self, 
   state: ChatState, 
   location_id: str
):
   try:
      return asyncio.run(_workflow_invoker(location_id=location_id, state=state))
   
   except Exception as exc:
      raise self.retry(exc=exc, countdown=5)
   