import asyncio
from pydantic import SecretStr
from src.workers.celery.app import worker
from src.chats.langgraph.workflows import compile_chat_workflow
from src.chats.schemas import ChatTaskPayload
from src.llm.langchain.models import get_model

@worker.task(name="chats.invoke_workflow", bind=True, max_retries=3)
def invoke_chat_workflow(self, payload: ChatTaskPayload):
   llm_config = payload["llm"]
   state = payload["state"]
   llm = get_model(
      model=llm_config["llm_model"],
      provider=llm_config["llm_provider"],
      api_key=SecretStr(llm_config["api_key"])
   )
   
   try:
      workflow = compile_chat_workflow(llm)
      return asyncio.run(workflow.ainvoke(state))
   
   except Exception as exc:
        raise self.retry(exc=exc, countdown=5)