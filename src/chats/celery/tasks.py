import asyncio
from pydantic import SecretStr
from src.workers.celery.app import worker
from src.chats.langgraph.workflows import compile_chat_workflow
from src.chats.schemas import ChatTaskPayload
from src.llm.langchain.models import get_model
from src.integrations.gohighlevel.client import GoHighLevelClient
from src.settings import settings

@worker.task(name="chats.invoke_workflow", bind=True, max_retries=3)
def invoke_chat_workflow(self, payload: ChatTaskPayload):
   if payload["ok_to_reply"]:
      state = payload["state"]
      llm = get_model(
         model="gpt-4o",
         provider="openai",
         api_key=SecretStr(settings.OPENAI_API_KEY)
      )
      
      try:
         workflow = compile_chat_workflow(llm)
         return asyncio.run(workflow.ainvoke(state))
      
      except Exception as exc:
         raise self.retry(exc=exc, countdown=5)
   
   return



@worker.task(name="chats.should_reply", bind=True, max_retries=3)
def should_reply(self, payload: ChatTaskPayload):
   ghl_client = GoHighLevelClient(payload["state"]["pit"])
   all_messages = asyncio.run(ghl_client.conversations.get_conversation_by_contact_id(payload["state"]["contact_id"]))
   
   payload["ok_to_reply"] = False

   return payload

   
    