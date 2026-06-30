import asyncio
from httpx import AsyncClient
from pydantic import SecretStr
from src.workers.celery.app import worker
from src.chats.langgraph.workflows import compile_chat_workflow
from src.chats.state import ChatState
from src.settings import settings
from src.cache.redis import RedisCacheStore
from src.integrations.gohighlevel.conversations import GHLConversationsClient
from src.cryptography.encryption import decrypt
from src.credentials.sqlalchemy.repository import get_by_external_id
from sqlalchemy.ext.asyncio import async_sessionmaker
from src.db.sqlalchemy.core import engine
from src.llm.langchain.agents import LangchainAgent
from src.llm.langchain.models import Provider
from src.embeddings.openai.service import OpenaiEmbeddingService
from src.vector_store.qdrant.vector_store import QdrantVectorStore


def _get_db_for_task():
   db_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
   return db_session_maker()


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
         url=settings.QDRANT_URL,
         api_key=settings.QDRANT_API_KEY,
         collection_name=settings.QDRANT_COLLECTION_NAME
      )

      cache_store = RedisCacheStore(connection_url=settings.REDIS_URL)
      db = _get_db_for_task()
      agent_credential = await get_by_external_id(db=db, external_id=location_id)

      if not agent_credential:
         raise ValueError(f"No credential found for location id: {agent_credential}")


      ghl_http = AsyncClient(
         base_url="https://services.leadconnectorhq.com",
         timeout=30.0,
      )
      
      ghl_headers = {
         "Authorization": f"Bearer {decrypt(agent_credential.access_token)}",
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
   