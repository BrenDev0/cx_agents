import asyncio
from pydantic import SecretStr
from src.workers.celery.app import worker
from src.chats.langgraph.workflows import compile_chat_workflow
from src.chats.state import ChatState
from src.llm.langchain.models import get_model
from src.settings import settings

@worker.task(name="chats.invoke_workflow", bind=True, max_retries=3)
def invoke_chat_workflow(self, state: ChatState):
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